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
  aws_account_id                 = "123456789012"
  aws_region                     = "us-east-1"
  availability_zone              = "us-east-1a"
  desktop_ssh_public_key         = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyForTerraformTests forge-dev-test"
  tailscale_federation_client_id = "synthetic-client-id"
  deployment_revision            = "0123456789abcdef0123456789abcdef01234567"
}

run "profile_in_bootstrap_payload" {
  command = apply

  assert {
    condition     = strcontains(data.cloudinit_config.dev_host.part[0].content, indent(6, local.host_tools_profile)) && strcontains(data.cloudinit_config.dev_host.part[0].content, indent(6, local.host_tools_helper))
    error_message = "Profile and stdlib helper must be embedded from the module's reviewed source."
  }
  assert {
    condition     = yamldecode(data.cloudinit_config.dev_host.part[0].content).write_files[0].content == local.host_tools_profile && yamldecode(data.cloudinit_config.dev_host.part[0].content).write_files[2].content == local.host_tools_helper
    error_message = "YAML literal embedding must preserve the profile and executable helper bytes."
  }
  assert {
    condition     = strcontains(data.cloudinit_config.dev_host.part[0].content, var.deployment_revision)
    error_message = "Receipt provenance must come from this deployment revision."
  }
  assert {
    condition     = length(data.cloudinit_config.dev_host.rendered) <= 21844
    error_message = "Compressed user data including profile/helper must fit EC2's decoded 16 KiB limit."
  }
  assert {
    condition     = aws_instance.dev_host.user_data_replace_on_change && aws_instance.dev_host.user_data_base64 == data.cloudinit_config.dev_host.rendered
    error_message = "Tool-profile delivery must retain the reviewed compute replacement path."
  }
  assert {
    condition     = can(regex("(?s)host-tools begin.*host-tools phase base-packages.*current_phase=\"forge-user\".*host-tools phase codex.*host-tools finish.*bootstrap-complete.json", local.bootstrap_script))
    error_message = "Whole-profile validation, installation identity and receipt completion ordering must be retained."
  }
}
