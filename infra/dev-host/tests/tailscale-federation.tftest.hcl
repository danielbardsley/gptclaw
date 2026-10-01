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

run "federation_bootstrap" {
  command = apply
  assert {
    condition     = strcontains(local.bootstrap_script, "python3 /usr/local/libexec/gptclaw-tailscale-federation") && !strcontains(local.bootstrap_script, "--auth-key") && !strcontains(local.bootstrap_script, "get-secret-value")
    error_message = "Bootstrap must use federation and never fall back to a stored key."
  }
  assert {
    condition = one([for s in jsondecode(aws_iam_role_policy.dev_host_runtime.policy).Statement :
      s.Condition["ForAllValues:StringEquals"]["sts:IdentityTokenAudience"] == local.tailscale_federation_audience &&
      s.Condition.Null["sts:IdentityTokenAudience"] == "false" &&
      s.Condition.NumericLessThanEquals["sts:DurationSeconds"] == 300 &&
      s.Condition.StringEquals["aws:RequestedRegion"] == "us-east-1" &&
      s.Action == ["sts:GetWebIdentityToken"] && s.Resource == "*"
      if s.Sid == "IssueTailscaleIdentityToken"
    ])
    error_message = "Only the exact audience, Region and <=300-second issuance may be granted."
  }
  assert {
    condition     = !strcontains(aws_iam_role_policy.dev_host_runtime.policy, "secretsmanager:") && !strcontains(aws_iam_role.dev_host.assume_role_policy, "AssumeRoleWithWebIdentity")
    error_message = "Host must lose secret reads and preserve EC2-only assumption."
  }
  assert {
    condition     = one([for f in yamldecode(data.cloudinit_config.dev_host.part[0].content).write_files : f.content if f.path == "/usr/local/libexec/gptclaw-tailscale-federation"]) == local.tailscale_federation_helper && length(data.cloudinit_config.dev_host.rendered) <= 21844
    error_message = "Exact helper bytes must fit the EC2 user-data limit."
  }
}
run "reject_unreviewed_tag" {
  command = plan
  variables { tailscale_tag = "tag:production" }
  expect_failures = [var.tailscale_tag]
}
