mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:user/terraform-test"
      user_id    = "AIDATEST"
    }
  }

  mock_data "aws_partition" {
    defaults = {
      partition          = "aws"
      dns_suffix         = "amazonaws.com"
      reverse_dns_prefix = "com.amazonaws"
    }
  }

  mock_data "aws_ssm_parameter" {
    defaults = {
      name  = "/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id"
      type  = "String"
      value = "ami-0123456789abcdef0"
    }
  }

  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{}"
    }
  }
}

provider "cloudinit" {}

override_resource {
  target = aws_iam_role.project_backups
  values = { arn = "arn:aws:iam::123456789012:role/gptclaw-dev-projects-backup" }
}

variables {
  android_runner_state           = "stopped"
  aws_account_id                 = "123456789012"
  aws_region                     = "us-east-1"
  availability_zone              = "us-east-1a"
  desktop_ssh_public_key         = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_federation_client_id = "synthetic-client-id"
  deployment_revision            = "0123456789abcdef0123456789abcdef01234567"
}

run "separate_private_runner" {
  command = apply
  assert {
    condition     = aws_instance.android_runner.instance_type == "m7i.xlarge" && aws_instance.android_runner.cpu_options[0].nested_virtualization == "enabled"
    error_message = "The test runner needs an explicitly supported KVM instance and enabled nested virtualization."
  }
  assert {
    condition     = aws_instance.dev_host.instance_type == "t3.large" && aws_volume_attachment.projects.instance_id == aws_instance.dev_host.id
    error_message = "The existing development host and project attachment must remain independent."
  }
  assert {
    condition     = aws_instance.android_runner.root_block_device[0].encrypted && aws_instance.android_runner.root_block_device[0].volume_size == 80 && aws_instance.android_runner.metadata_options[0].http_tokens == "required"
    error_message = "The runner must use encrypted bounded storage and IMDSv2."
  }
  assert {
    condition     = aws_instance.android_runner.vpc_security_group_ids == toset([aws_security_group.dev_host.id]) && aws_instance.android_runner.iam_instance_profile == aws_iam_instance_profile.dev_host.name
    error_message = "Reuse existing private networking and the scoped development identity without IAM expansion."
  }
  assert {
    condition     = aws_ec2_instance_state.android_runner.state == "stopped"
    error_message = "Default runner state must avoid unattended compute use."
  }
  assert {
    condition     = length(data.cloudinit_config.android_runner.rendered) < 21844
    error_message = "Compressed EC2 bootstrap must fit the user-data API limit."
  }
}
run "explicit_running_session" {
  command = plan
  variables { android_runner_state = "running" }
  assert {
    condition     = aws_ec2_instance_state.android_runner.state == "running"
    error_message = "An authorized workflow must be able to start the test runner."
  }
}
run "reject_unrecognized_state" {
  command = plan
  variables { android_runner_state = "terminated" }
  expect_failures = [var.android_runner_state]
}
