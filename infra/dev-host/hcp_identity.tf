locals {
  hcp_oidc_provider_url = "https://app.terraform.io"
  hcp_oidc_audience     = "aws.workload.identity"
  hcp_subject_prefix    = "organization:${var.hcp_terraform_organization}:project:${var.hcp_terraform_project}:workspace:${var.hcp_terraform_workspace}:run_phase"

  backup_name     = "${local.name_prefix}-projects-backup"
  backup_role_arn = "arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.backup_name}"
  backup_dlm_arn  = "arn:${data.aws_partition.current.partition}:dlm:${var.aws_region}:${var.aws_account_id}:policy/*"
}

resource "aws_iam_openid_connect_provider" "hcp_terraform" {
  url            = local.hcp_oidc_provider_url
  client_id_list = [local.hcp_oidc_audience]

  lifecycle {
    prevent_destroy = true

    # This provider is the trust anchor used to obtain the apply role itself.
    # Keep its creation-time tags stable so routine deployment-revision changes
    # do not require the apply role to mutate its own authentication bootstrap.
    ignore_changes = [tags]
  }

  tags = {
    Name = "${local.name_prefix}-hcp-terraform"
  }
}

resource "aws_iam_role" "hcp_plan" {
  name = "${local.name_prefix}-hcp-plan"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.hcp_terraform.arn }
      Condition = {
        StringEquals = {
          "app.terraform.io:aud" = local.hcp_oidc_audience
          "app.terraform.io:sub" = "${local.hcp_subject_prefix}:plan"
        }
      }
    }]
  })

  lifecycle {
    prevent_destroy = true

    # This bootstrap role cannot safely require permission to retag itself.
    ignore_changes = [tags]
  }

  tags = {
    Name = "${local.name_prefix}-hcp-plan"
  }
}

resource "aws_iam_role" "hcp_apply" {
  name = "${local.name_prefix}-hcp-apply"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.hcp_terraform.arn }
      Condition = {
        StringEquals = {
          "app.terraform.io:aud" = local.hcp_oidc_audience
          "app.terraform.io:sub" = "${local.hcp_subject_prefix}:apply"
        }
      }
    }]
  })

  lifecycle {
    prevent_destroy = true

    # This bootstrap role cannot safely require permission to retag itself.
    ignore_changes = [tags]
  }

  tags = {
    Name = "${local.name_prefix}-hcp-apply"
  }
}

data "aws_iam_policy_document" "hcp_plan" {
  statement {
    sid    = "DiscoverDevelopmentInfrastructure"
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "logs:DescribeLogGroups",
      "sts:GetCallerIdentity",
    ]
    resources = ["*"]
  }

  statement {
    sid       = "ReadCanonicalUbuntuAmi"
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:${data.aws_partition.current.partition}:ssm:${var.aws_region}::parameter/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id"]
  }

  statement {
    sid    = "ReadDeploymentIdentities"
    effect = "Allow"
    actions = [
      "iam:GetInstanceProfile",
      "iam:GetOpenIDConnectProvider",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListInstanceProfileTags",
      "iam:ListInstanceProfilesForRole",
      "iam:ListOpenIDConnectProviderTags",
      "iam:ListRolePolicies",
      "iam:ListRoleTags",
    ]
    resources = [
      aws_iam_openid_connect_provider.hcp_terraform.arn,
      aws_iam_role.hcp_plan.arn,
      aws_iam_role.hcp_apply.arn,
      local.backup_role_arn,
      "arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host",
      "arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:instance-profile/${local.name_prefix}-host",
    ]
  }

  statement {
    sid    = "ReadDevelopmentLogsAndEnrollmentSecret"
    effect = "Allow"
    actions = [
      "logs:ListTagsForResource",
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:ListSecretVersionIds",
    ]
    resources = [
      aws_cloudwatch_log_group.dev_host.arn,
      aws_secretsmanager_secret.tailscale_enrollment.arn,
    ]
  }

  statement {
    sid       = "ReadBackupPolicies"
    actions   = ["dlm:GetLifecyclePolicy", "dlm:ListTagsForResource"]
    resources = [local.backup_dlm_arn]
  }


}

resource "aws_iam_role_policy" "hcp_plan" {
  name   = "${local.name_prefix}-terraform-plan"
  role   = aws_iam_role.hcp_plan.id
  policy = data.aws_iam_policy_document.hcp_plan.json

  lifecycle {
    prevent_destroy = true
  }
}

data "aws_iam_policy_document" "hcp_apply" {
  source_policy_documents = [data.aws_iam_policy_document.hcp_plan.json]

  statement {
    sid    = "ManageDevelopmentEc2Resources"
    effect = "Allow"
    actions = [
      "ec2:AssociateRouteTable",
      "ec2:AttachInternetGateway",
      "ec2:AttachVolume",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:CreateInternetGateway",
      "ec2:CreateRoute",
      "ec2:CreateRouteTable",
      "ec2:CreateSecurityGroup",
      "ec2:CreateSubnet",
      "ec2:CreateTags",
      "ec2:CreateVolume",
      "ec2:CreateVpc",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteRoute",
      "ec2:DeleteRouteTable",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteSubnet",
      "ec2:DeleteTags",
      "ec2:DeleteVolume",
      "ec2:DeleteVpc",
      "ec2:DetachInternetGateway",
      "ec2:DetachVolume",
      "ec2:DisassociateRouteTable",
      "ec2:ModifyInstanceAttribute",
      "ec2:ModifyInstanceMetadataOptions",
      "ec2:ModifySubnetAttribute",
      "ec2:ModifyVolume",
      "ec2:ModifyVpcAttribute",
      "ec2:ReplaceRoute",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RunInstances",
      "ec2:StartInstances",
      "ec2:StopInstances",
      "ec2:TerminateInstances",
    ]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = [var.aws_region]
    }
  }

  statement {
    sid    = "ManageDevelopmentHostRole"
    effect = "Allow"
    actions = [
      "iam:AttachRolePolicy",
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:DeleteRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PutRolePolicy",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",
    ]
    resources = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host"]
  }

  statement {
    sid    = "ManageDevelopmentHostInstanceProfile"
    effect = "Allow"
    actions = [
      "iam:AddRoleToInstanceProfile",
      "iam:CreateInstanceProfile",
      "iam:DeleteInstanceProfile",
      "iam:RemoveRoleFromInstanceProfile",
      "iam:TagInstanceProfile",
      "iam:UntagInstanceProfile",
    ]
    resources = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:instance-profile/${local.name_prefix}-host"]
  }

  statement {
    sid       = "PassDevelopmentHostRoleOnly"
    effect    = "Allow"
    actions   = ["iam:PassRole"]
    resources = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host"]

    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["ec2.amazonaws.com"]
    }
  }

  statement {
    sid    = "ManageDevelopmentLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:PutRetentionPolicy",
      "logs:TagResource",
      "logs:UntagResource",
    ]
    resources = ["arn:${data.aws_partition.current.partition}:logs:${var.aws_region}:${var.aws_account_id}:log-group:/${var.project_name}/${var.environment}/${var.instance_name}*"]
  }

  statement {
    sid    = "ManageTailscaleEnrollmentSecret"
    effect = "Allow"
    actions = [
      "secretsmanager:PutSecretValue",
      "secretsmanager:TagResource",
      "secretsmanager:UntagResource",
      "secretsmanager:UpdateSecret",
    ]
    resources = [aws_secretsmanager_secret.tailscale_enrollment.arn]
  }


  statement {
    sid       = "CreateTaggedBackupPolicy"
    actions   = ["dlm:CreateLifecyclePolicy"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = [var.aws_region]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/BackupSet"
      values   = ["${var.environment}-projects"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/Project"
      values   = ["GptClaw"]
    }
  }

  statement {
    sid       = "ManageBackupPolicy"
    actions   = ["dlm:UpdateLifecyclePolicy", "dlm:DeleteLifecyclePolicy", "dlm:TagResource", "dlm:UntagResource"]
    resources = [local.backup_dlm_arn]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/BackupSet"
      values   = ["${var.environment}-projects"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Project"
      values   = ["GptClaw"]
    }
  }

  statement {
    sid = "ManageBackupRole"
    actions = [
      "iam:CreateRole", "iam:DeleteRole", "iam:PutRolePolicy",
      "iam:DeleteRolePolicy", "iam:TagRole", "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",
    ]
    resources = [local.backup_role_arn]
  }

  statement {
    sid       = "PassBackupRoleToDlm"
    actions   = ["iam:PassRole"]
    resources = [local.backup_role_arn]

    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["dlm.amazonaws.com"]
    }
  }


}

resource "aws_iam_role_policy" "hcp_apply" {
  name   = "${local.name_prefix}-terraform-apply"
  role   = aws_iam_role.hcp_apply.id
  policy = data.aws_iam_policy_document.hcp_apply.json

  lifecycle {
    prevent_destroy = true
  }
}
