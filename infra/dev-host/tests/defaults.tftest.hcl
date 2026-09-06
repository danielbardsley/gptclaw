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

variables {
  aws_account_id         = "123456789012"
  aws_region             = "us-east-1"
  availability_zone      = "us-east-1a"
  desktop_ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_auth_key     = "tskey-auth-test"
  deployment_revision    = "0123456789abcdef0123456789abcdef01234567"
}

run "planned_defaults" {
  command = plan

  assert {
    condition     = aws_instance.dev_host.instance_type == "t3.large"
    error_message = "The default instance type must remain t3.large."
  }

  assert {
    condition     = aws_instance.dev_host.availability_zone == "us-east-1a"
    error_message = "The host must be created in the selected availability zone."
  }

  assert {
    condition     = aws_ebs_volume.projects.size == 80
    error_message = "The default project volume must remain 80 GiB."
  }

  assert {
    condition     = aws_cloudwatch_log_group.dev_host.retention_in_days == 14
    error_message = "The default log retention must remain 14 days."
  }

  assert {
    condition     = output.expected_tailscale_hostname == "forge-dev-01"
    error_message = "The expected Tailscale hostname must match the instance name."
  }

  assert {
    condition     = output.deployment_revision == "0123456789abcdef0123456789abcdef01234567"
    error_message = "The deployment revision output must retain the workflow SHA."
  }

  assert {
    condition     = aws_secretsmanager_secret_version.tailscale_enrollment.secret_string_wo_version == 2
    error_message = "The default Tailscale secret version must match the committed rotation counter."
  }
}
