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
  aws_account_id         = "123456789012"
  aws_region             = "us-east-1"
  availability_zone      = "us-east-1a"
  desktop_ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_auth_key     = "tskey-auth-test"
  deployment_revision    = "0123456789abcdef0123456789abcdef01234567"
}

run "initial_identity_state" {
  command = apply
}

run "retag_keeps_deployment_policies_known" {
  command = plan
  variables {
    deployment_revision = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  }
  assert {
    condition     = length(jsondecode(aws_iam_role_policy.hcp_plan.policy).Statement) == 5 && length(jsondecode(aws_iam_role_policy.hcp_apply.policy).Statement) == 15
    error_message = "A revision-only retag must leave deployment policy JSON known during plan."
  }
  assert {
    condition = alltrue([for s in jsondecode(aws_iam_role_policy.hcp_apply.policy).Statement :
      !anytrue([for a in s.Action : startswith(a, "iam:") && !can(regex(":(Get|List)", a))]) ||
      alltrue([for arn in s.Resource : contains([
        "arn:aws:iam::123456789012:role/gptclaw-dev-host",
        "arn:aws:iam::123456789012:instance-profile/gptclaw-dev-host",
        "arn:aws:iam::123456789012:role/gptclaw-dev-projects-backup"
      ], arn)])
    ])
    error_message = "Rendered apply policy must not acquire identity self-management."
  }
}
