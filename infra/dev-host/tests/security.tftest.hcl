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

run "security_controls" {
  command = apply

  assert {
    condition     = length(aws_security_group.dev_host.ingress) == 0
    error_message = "The host security group must not have inbound rules."
  }

  assert {
    condition     = aws_ebs_volume.projects.encrypted
    error_message = "The persistent project volume must be encrypted."
  }

  assert {
    condition     = aws_ebs_volume.projects.availability_zone == aws_instance.dev_host.availability_zone
    error_message = "Compute and persistent project storage must share an availability zone."
  }

  assert {
    condition     = aws_instance.dev_host.root_block_device[0].encrypted
    error_message = "The instance root volume must be encrypted."
  }

  assert {
    condition     = aws_instance.dev_host.metadata_options[0].http_tokens == "required"
    error_message = "IMDSv2 tokens must be required."
  }

  assert {
    condition     = aws_instance.dev_host.metadata_options[0].http_put_response_hop_limit == 1
    error_message = "The metadata response hop limit must remain one."
  }

  assert {
    condition     = aws_instance.dev_host.user_data_replace_on_change
    error_message = "Bootstrap changes must trigger reviewed compute replacement."
  }

  assert {
    condition     = local.common_tags["DeploymentRevision"] == "0123456789abcdef0123456789abcdef01234567"
    error_message = "Resources must retain deployment revision traceability."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.dev_host_runtime.policy, aws_secretsmanager_secret.tailscale_enrollment.arn)
    error_message = "The host role must be limited to the exact Tailscale secret."
  }

  assert {
    condition     = strcontains(aws_iam_role.hcp_plan.assume_role_policy, "organization:Bardsley:project:gptclaw:workspace:gptclaw-dev-host:run_phase:plan")
    error_message = "The plan role trust must be limited to the exact HCP plan subject."
  }

  assert {
    condition     = strcontains(aws_iam_role.hcp_apply.assume_role_policy, "organization:Bardsley:project:gptclaw:workspace:gptclaw-dev-host:run_phase:apply")
    error_message = "The apply role trust must be limited to the exact HCP apply subject."
  }

  assert {
    condition     = aws_iam_openid_connect_provider.hcp_terraform.client_id_list == toset(["aws.workload.identity"])
    error_message = "The HCP OIDC provider must accept only the workload identity audience."
  }
}

run "reject_wrong_account" {
  command = plan

  variables {
    aws_account_id = "999999999999"
  }

  expect_failures = [check.target_account]
}

run "reject_private_ssh_key" {
  command = plan

  variables {
    desktop_ssh_public_key = "not-a-public-key"
  }

  expect_failures = [var.desktop_ssh_public_key]
}

run "reject_invalid_tailscale_key" {
  command = plan

  variables {
    tailscale_auth_key = "not-a-tailscale-key"
  }

  expect_failures = [var.tailscale_auth_key]
}
