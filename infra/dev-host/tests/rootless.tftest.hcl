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

run "rootless_pipeline_bootstrap" {
  command = apply
  assert {
    condition     = yamldecode(data.cloudinit_config.dev_host.part[0].content).write_files[3].content == local.rootless_helper
    error_message = "Rootless helper must be embedded byte-for-byte from the reviewed module source."
  }
  assert {
    condition     = [for entry in yamldecode(data.cloudinit_config.dev_host.part[0].content).write_files : entry.content if entry.path == "/usr/local/sbin/gptclaw-bootstrap"][0] == local.bootstrap_script
    error_message = "Literal YAML embedding must preserve the complete bootstrap bytes."
  }
  assert {
    condition     = can(regex("(?s)rootless prepare.*host-tools phase base-packages.*rootless identity.*current_phase=\"project-volume\".*rootless configure.*rootless verify.*host-tools finish.*bootstrap-complete.json", local.bootstrap_script))
    error_message = "Identity, mount readiness, capabilities and receipt completion must be correctly ordered."
  }
  assert {
    condition     = length(data.cloudinit_config.dev_host.rendered) <= 21844
    error_message = "Full rootless provisioning payload must fit the existing EC2 user-data limit."
  }
  assert {
    condition     = aws_instance.dev_host.user_data_replace_on_change && aws_instance.dev_host.user_data_base64 == data.cloudinit_config.dev_host.rendered
    error_message = "Rootless provisioning remains on the protected replacement path."
  }
  assert {
    condition     = strcontains(local.rootless_helper, "UID = GID = 1002") && strcontains(local.rootless_helper, "231072, 65536")
    error_message = "Preserve the observed forge identity and subordinate allocation across replacement."
  }
}
