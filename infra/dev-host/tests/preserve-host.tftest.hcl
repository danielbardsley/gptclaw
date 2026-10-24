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

mock_provider "cloudinit" {}

override_resource {
  target = aws_iam_role.project_backups
  values = { arn = "arn:aws:iam::123456789012:role/gptclaw-dev-projects-backup" }
}

variables {
  aws_account_id                 = "123456789012"
  aws_region                     = "us-east-1"
  availability_zone              = "us-east-1a"
  desktop_ssh_public_key         = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_federation_client_id = "synthetic-client-id"
  deployment_revision            = "0123456789abcdef0123456789abcdef01234567"
}

run "existing_host" {
  command = apply

  variables {
    root_volume_size_gib = 30
  }

  override_data {
    target = data.cloudinit_config.dev_host
    values = { rendered = "aW5pdGlhbA==" }
  }
}

run "resize_with_bootstrap_and_ami_drift" {
  command = plan

  variables {
    root_volume_size_gib = 1024
    deployment_revision  = "fedcba9876543210fedcba9876543210fedcba98"
  }

  override_data {
    target = data.aws_ssm_parameter.ubuntu_ami
    values = { value = "ami-0fedcba9876543210" }
  }

  override_data {
    target = data.cloudinit_config.dev_host
    values = { rendered = "Y2hhbmdlZA==" }
  }

  assert {
    condition     = aws_instance.dev_host.id == run.existing_host.instance_id
    error_message = "Root-volume growth must preserve the existing instance."
  }

  assert {
    condition     = aws_instance.dev_host.root_block_device[0].volume_size == 1024
    error_message = "The existing root volume must grow to 1 TiB."
  }

  assert {
    condition     = aws_instance.dev_host.ami == "ami-0123456789abcdef0" && aws_instance.dev_host.user_data_base64 == "aW5pdGlhbA=="
    error_message = "AMI and bootstrap drift must not change the existing host."
  }

  assert {
    condition     = aws_volume_attachment.projects.instance_id == run.existing_host.instance_id && aws_ebs_volume.projects.id == run.existing_host.data_volume_id
    error_message = "The project disk and its existing attachment must be retained."
  }
}

