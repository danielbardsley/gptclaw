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
      for statement in data.aws_iam_policy_document.hcp_plan.statement :
      alltrue([for action in statement.actions : can(regex(":(Get|List|Describe)", action))])
    ])
    error_message = "The plan role must remain read-only."
  }
  assert {
    condition = alltrue([
      for statement in data.aws_iam_policy_document.hcp_apply.statement :
      !anytrue([for action in statement.actions : startswith(action, "iam:")]) ||
      alltrue([for arn in statement.resources : contains([
        "arn:aws:iam::123456789012:role/gptclaw-dev-host",
        "arn:aws:iam::123456789012:instance-profile/gptclaw-dev-host",
        "arn:aws:iam::123456789012:role/gptclaw-dev-projects-backup",
      ], arn)])
    ])
    error_message = "Apply IAM mutations must never include deployment roles, OIDC, or arbitrary roles."
  }
  assert {
    condition = one([
      for statement in data.aws_iam_policy_document.hcp_apply.statement :
      statement.resources == toset([local.backup_role_arn]) &&
      anytrue([for condition in statement.condition :
        condition.variable == "iam:PassedToService" && condition.values == toset(["dlm.amazonaws.com"])
      ])
      if statement.sid == "PassBackupRoleToDlm"
    ])
    error_message = "The backup role can be passed only to DLM."
  }
  assert {
    condition = one([
      for statement in data.aws_iam_policy_document.hcp_apply.statement :
      alltrue([for key in ["aws:ResourceTag/Project", "aws:ResourceTag/BackupSet"] :
        contains([for condition in statement.condition : condition.variable], key)
      ]) && statement.resources == toset([local.backup_dlm_arn])
      if statement.sid == "ManageBackupPolicy"
    ])
    error_message = "DLM management must be scoped to this Region/account and backup tags."
  }
  assert {
    condition = one([
      for statement in data.aws_iam_policy_document.hcp_apply.statement :
      alltrue([for key in ["aws:RequestedRegion", "aws:RequestTag/Project", "aws:RequestTag/BackupSet"] :
        contains([for condition in statement.condition : condition.variable], key)
      ]) && statement.actions == toset(["dlm:CreateLifecyclePolicy"])
      if statement.sid == "CreateTaggedBackupPolicy"
    ])
    error_message = "Wildcard DLM creation must be constrained by Region and request tags."
  }
  assert {
    condition = alltrue([
      for statement in concat(
        tolist(data.aws_iam_policy_document.hcp_plan.statement),
        tolist(data.aws_iam_policy_document.hcp_apply.statement)
      ) :
      !anytrue([for action in statement.actions : startswith(action, "sns:")]) ||
      statement.resources == toset([local.backup_topic_arn])
    ])
    error_message = "SNS actions, including subscription operations, must use the exact topic ARN."
  }
  assert {
    condition = !anytrue([
      for statement in data.aws_iam_policy_document.hcp_apply.statement :
      anytrue([for action in statement.actions :
        contains(["ec2:CreateSnapshot", "ec2:DeleteSnapshot", "cloudwatch:PutMetricData", "lambda:CreateFunction"], action)
      ])
    ])
    error_message = "Snapshot lifecycle belongs to DLM; no custom monitor permissions may be added."
  }
}
