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

locals {
  hcp_plan_statements = [
    {
      Sid    = "DiscoverDevelopmentInfrastructure"
      Effect = "Allow"
      Action = [
        "ec2:Describe*",
        "logs:DescribeLogGroups",
        "sts:GetCallerIdentity",
      ]
      Resource = ["*"]
    },
    {
      Sid      = "ReadCanonicalUbuntuAmi"
      Effect   = "Allow"
      Action   = ["ssm:GetParameter"]
      Resource = ["arn:${data.aws_partition.current.partition}:ssm:${var.aws_region}::parameter/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id"]
    },
    {
      Sid    = "ReadDeploymentIdentities"
      Effect = "Allow"
      Action = [
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
      Resource = [
        aws_iam_openid_connect_provider.hcp_terraform.arn,
        aws_iam_role.hcp_plan.arn,
        aws_iam_role.hcp_apply.arn,
        local.backup_role_arn,
        "arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host",
        "arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:instance-profile/${local.name_prefix}-host",
      ]
    },
    {
      Sid    = "ReadDevelopmentLogsAndEnrollmentSecret"
      Effect = "Allow"
      Action = [
        "logs:ListTagsForResource",
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetResourcePolicy",
        "secretsmanager:ListSecretVersionIds",
      ]
      Resource = [
        aws_cloudwatch_log_group.dev_host.arn,
        aws_secretsmanager_secret.tailscale_enrollment.arn,
      ]
    },
    {
      Sid      = "ReadBackupPolicies"
      Action   = ["dlm:GetLifecyclePolicy", "dlm:ListTagsForResource"]
      Resource = [local.backup_dlm_arn]
      Effect   = "Allow"
    },
  ]
}

resource "aws_iam_role_policy" "hcp_plan" {
  name   = "${local.name_prefix}-terraform-plan"
  role   = aws_iam_role.hcp_plan.id
  policy = local.hcp_plan_policy

  lifecycle {
    prevent_destroy = true
  }
}

locals {
  hcp_apply_statements = [
    {
      Sid    = "ManageDevelopmentEc2Resources"
      Effect = "Allow"
      Action = [
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
      Resource = ["*"]

      Condition = { StringEquals = {
        "aws:RequestedRegion" = var.aws_region
      } }
    },
    {
      Sid    = "ManageDevelopmentHostRole"
      Effect = "Allow"
      Action = [
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
      Resource = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host"]
    },
    {
      Sid    = "ManageDevelopmentHostInstanceProfile"
      Effect = "Allow"
      Action = [
        "iam:AddRoleToInstanceProfile",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile",
        "iam:TagInstanceProfile",
        "iam:UntagInstanceProfile",
      ]
      Resource = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:instance-profile/${local.name_prefix}-host"]
    },
    {
      Sid      = "PassDevelopmentHostRoleOnly"
      Effect   = "Allow"
      Action   = ["iam:PassRole"]
      Resource = ["arn:${data.aws_partition.current.partition}:iam::${var.aws_account_id}:role/${local.name_prefix}-host"]

      Condition = { StringEquals = {
        "iam:PassedToService" = "ec2.amazonaws.com"
      } }
    },
    {
      Sid    = "ManageDevelopmentLogs"
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy",
        "logs:TagResource",
        "logs:UntagResource",
      ]
      Resource = ["arn:${data.aws_partition.current.partition}:logs:${var.aws_region}:${var.aws_account_id}:log-group:/${var.project_name}/${var.environment}/${var.instance_name}*"]
    },
    {
      Sid    = "ManageTailscaleEnrollmentSecret"
      Effect = "Allow"
      Action = [
        "secretsmanager:PutSecretValue",
        "secretsmanager:TagResource",
        "secretsmanager:UntagResource",
        "secretsmanager:UpdateSecret",
      ]
      Resource = [aws_secretsmanager_secret.tailscale_enrollment.arn]
    },
    {
      Sid      = "CreateTaggedBackupPolicy"
      Action   = ["dlm:CreateLifecyclePolicy"]
      Resource = ["*"]

      Effect = "Allow"
      Condition = { StringEquals = {
        "aws:RequestedRegion"      = var.aws_region
        "aws:RequestTag/BackupSet" = "${var.environment}-projects"
        "aws:RequestTag/Project"   = "GptClaw"
      } }
    },
    {
      Sid      = "ManageBackupPolicy"
      Action   = ["dlm:UpdateLifecyclePolicy", "dlm:DeleteLifecyclePolicy", "dlm:TagResource", "dlm:UntagResource"]
      Resource = [local.backup_dlm_arn]

      Effect = "Allow"
      Condition = { StringEquals = {
        "aws:ResourceTag/BackupSet" = "${var.environment}-projects"
        "aws:ResourceTag/Project"   = "GptClaw"
      } }
    },
    {
      Sid = "ManageBackupRole"
      Action = [
        "iam:CreateRole", "iam:DeleteRole", "iam:PutRolePolicy",
        "iam:DeleteRolePolicy", "iam:TagRole", "iam:UntagRole",
        "iam:UpdateAssumeRolePolicy",
      ]
      Resource = [local.backup_role_arn]
      Effect   = "Allow"
    },
    {
      Sid      = "PassBackupRoleToDlm"
      Action   = ["iam:PassRole"]
      Resource = [local.backup_role_arn]

      Effect = "Allow"
      Condition = { StringEquals = {
        "iam:PassedToService" = "dlm.amazonaws.com"
      } }
    },
  ]
}

resource "aws_iam_role_policy" "hcp_apply" {
  name   = "${local.name_prefix}-terraform-apply"
  role   = aws_iam_role.hcp_apply.id
  policy = local.hcp_apply_policy

  lifecycle {
    prevent_destroy = true
  }
}

# Render policy JSON locally: provider data-source reads defer when referenced
# resources are retagged, spuriously planning protected identity policy writes.
# These expressions retain the exact resource ARNs and existing permissions.
locals {
  hcp_plan_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = local.hcp_plan_statements
  })
  hcp_apply_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = concat(local.hcp_plan_statements, local.hcp_apply_statements)
  })
}
