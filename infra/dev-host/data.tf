data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_ssm_parameter" "ubuntu_ami" {
  name = "/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

check "target_account" {
  assert {
    condition     = data.aws_caller_identity.current.account_id == var.aws_account_id
    error_message = "The active AWS identity does not belong to the approved account."
  }
}

check "target_availability_zone" {
  assert {
    condition     = startswith(var.availability_zone, var.aws_region)
    error_message = "The selected availability zone does not belong to the approved region."
  }
}

check "tailscale_secret_scope" {
  assert {
    condition = (
      strcontains(var.tailscale_auth_secret_arn, ":${var.aws_region}:") &&
      strcontains(var.tailscale_auth_secret_arn, ":${var.aws_account_id}:")
    )
    error_message = "The Tailscale secret must be in the approved AWS account and region."
  }
}
