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
  aws_account_id         = "123456789012"
  aws_region             = "us-east-1"
  availability_zone      = "us-east-1a"
  desktop_ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_auth_key     = "tskey-auth-test"
  deployment_revision    = "0123456789abcdef0123456789abcdef01234567"
}

run "first_boot_policy" {
  command = apply

  assert {
    condition     = output.host_policy_revision == "a287d7c9712817fd9f318a11f28041cfc6b5ad06"
    error_message = "First boot must use the explicitly reviewed policy revision."
  }

  assert {
    condition     = strcontains(local.host_policy_script, var.host_policy_revision) && !strcontains(local.host_policy_script, var.deployment_revision)
    error_message = "Policy source must be pinned independently of each deployment revision."
  }

  assert {
    condition     = strcontains(local.host_policy_script, "https://github.com/danielbardsley/gptclaw.git") && strcontains(local.host_policy_script, "FETCH_HEAD^{commit}")
    error_message = "Bootstrap must fetch the fixed public source and verify the commit pin."
  }

  assert {
    condition     = can(regex("(?s)current_phase=\"host-policy\".*sudo -iu forge /usr/local/libexec/gptclaw-install-host-policy.*current_phase=\"codex\"", local.bootstrap_script))
    error_message = "Policy installation must run as forge before Codex and bootstrap completion."
  }

  assert {
    condition     = strcontains(data.cloudinit_config.dev_host.part[0].content, base64encode(local.host_policy_script))
    error_message = "Cloud-init must embed the generated policy bootstrap helper."
  }

  assert {
    condition     = length(data.cloudinit_config.dev_host.rendered) <= 21844
    error_message = "Compressed base64 user data must fit conservatively within EC2's 16 KiB decoded limit."
  }

  assert {
    condition     = aws_instance.dev_host.user_data_replace_on_change && aws_instance.dev_host.user_data_base64 == data.cloudinit_config.dev_host.rendered
    error_message = "Policy bootstrap remains on the reviewed user-data replacement path."
  }
}

run "explicit_pin_override" {
  command = plan
  variables {
    host_policy_revision = "1111111111111111111111111111111111111111"
    deployment_revision  = "2222222222222222222222222222222222222222"
  }
  assert {
    condition     = strcontains(local.host_policy_script, var.host_policy_revision) && !strcontains(local.host_policy_script, var.deployment_revision)
    error_message = "An explicit pin override must remain independent of deployment tags."
  }
}

run "reject_mutable_pin" {
  command = plan
  variables {
    host_policy_revision = "main"
  }
  expect_failures = [var.host_policy_revision]
}
