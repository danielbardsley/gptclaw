mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = { account_id = "123456789012" }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws", dns_suffix = "amazonaws.com" }
  }
  mock_data "aws_ssm_parameter" {
    defaults = { value = "ami-0123456789abcdef0" }
  }
  mock_data "aws_iam_policy_document" {
    defaults = { json = "{}" }
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

run "backup_deployment_boundaries" {
  command = plan

  assert {
    condition = alltrue([
      for statement in local.hcp_plan_statements :
      alltrue([for action in statement.Action : can(regex(":(Get|List|Describe)", action))])
    ])
    error_message = "The plan role must remain read-only."
  }
  assert {
    condition = alltrue([
      for statement in local.hcp_apply_statements :
      !anytrue([for action in statement.Action : startswith(action, "iam:")]) ||
      alltrue([for arn in statement.Resource : contains([
        "arn:aws:iam::123456789012:role/gptclaw-dev-host",
        "arn:aws:iam::123456789012:instance-profile/gptclaw-dev-host",
        "arn:aws:iam::123456789012:role/gptclaw-dev-projects-backup",
      ], arn)])
    ])
    error_message = "Apply IAM mutations must never include deployment roles, OIDC, or arbitrary roles."
  }
  assert {
    condition = one([
      for statement in local.hcp_apply_statements :
      toset(statement.Resource) == toset([local.backup_role_arn]) &&
      statement.Condition.StringEquals["iam:PassedToService"] == "dlm.amazonaws.com"
      if statement.Sid == "PassBackupRoleToDlm"
    ])
    error_message = "The backup role can be passed only to DLM."
  }
  assert {
    condition = one([
      for statement in local.hcp_apply_statements :
      alltrue([for key in ["aws:ResourceTag/Project", "aws:ResourceTag/BackupSet"] :
        contains(keys(statement.Condition.StringEquals), key)
      ]) && toset(statement.Resource) == toset([local.backup_dlm_arn])
      if statement.Sid == "ManageBackupPolicy"
    ])
    error_message = "DLM management must be scoped to this Region/account and backup tags."
  }
  assert {
    condition = one([
      for statement in local.hcp_apply_statements :
      alltrue([for key in ["aws:RequestedRegion", "aws:RequestTag/Project", "aws:RequestTag/BackupSet"] :
        contains(keys(statement.Condition.StringEquals), key)
      ]) && toset(statement.Action) == toset(["dlm:CreateLifecyclePolicy"])
      if statement.Sid == "CreateTaggedBackupPolicy"
    ])
    error_message = "Wildcard DLM creation must be constrained by Region and request tags."
  }
  assert {
    condition = !anytrue([
      for statement in local.hcp_apply_statements :
      anytrue([for action in statement.Action :
        contains(["ec2:CreateSnapshot", "ec2:DeleteSnapshot"], action) ||
        can(regex("^(sns|cloudwatch|lambda|events):", action))
      ])
    ])
    error_message = "Snapshot lifecycle belongs to DLM; no notification or monitor permissions may be added."
  }
}
