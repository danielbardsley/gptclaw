locals {
  backup_selection_tag = { GptClawBackup = "${var.environment}-projects" }
  backup_snapshot_arn  = "arn:${data.aws_partition.current.partition}:ec2:${var.aws_region}::snapshot/*"
  backup_volume_arn    = "arn:${data.aws_partition.current.partition}:ec2:${var.aws_region}:${var.aws_account_id}:volume/${aws_ebs_volume.projects.id}"
}

resource "aws_iam_role" "project_backups" {
  name = local.backup_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "dlm.amazonaws.com" }
      Condition = {
        StringEquals = { "aws:SourceAccount" = var.aws_account_id }
        ArnLike      = { "aws:SourceArn" = local.backup_dlm_arn }
      }
    }]
  })

  tags = { Name = local.backup_name }
}

resource "aws_iam_role_policy" "project_backup_creation" {
  name = "${local.backup_name}-creation"
  role = aws_iam_role.project_backups.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "DiscoverSnapshotMetadata"
        Effect   = "Allow"
        Action   = ["ec2:DescribeVolumes", "ec2:DescribeSnapshots"]
        Resource = "*"
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
      {
        Sid      = "SnapshotProjectVolume"
        Effect   = "Allow"
        Action   = "ec2:CreateSnapshot"
        Resource = local.backup_volume_arn
      },
      {
        Sid      = "CreateSnapshotResource"
        Effect   = "Allow"
        Action   = "ec2:CreateSnapshot"
        Resource = local.backup_snapshot_arn
      },
      {
        Sid      = "TagSnapshotAtCreation"
        Effect   = "Allow"
        Action   = "ec2:CreateTags"
        Resource = local.backup_snapshot_arn
        Condition = {
          StringEquals = { "ec2:CreateAction" = "CreateSnapshot" }
        }
      },
    ]
  })
}

resource "aws_dlm_lifecycle_policy" "projects" {
  description        = "Encrypted project-volume snapshots with count retention"
  execution_role_arn = aws_iam_role.project_backups.arn
  state              = var.backup_policy_enabled ? "ENABLED" : "DISABLED"

  policy_details {
    policy_type        = "EBS_SNAPSHOT_MANAGEMENT"
    resource_types     = ["VOLUME"]
    resource_locations = ["CLOUD"]
    target_tags        = local.backup_selection_tag

    schedule {
      name      = "projects-daily"
      copy_tags = false

      create_rule {
        interval      = var.backup_interval_hours
        interval_unit = "HOURS"
        times         = [var.backup_start_time_utc]
      }

      retain_rule {
        count = var.backup_retention_count
      }

      tags_to_add = {
        Project        = local.common_tags.Project
        Environment    = var.environment
        Repository     = local.common_tags.Repository
        BackupSet      = "${var.environment}-projects"
        RetentionClass = "daily"
      }
    }
  }

  tags = {
    Name      = local.backup_name
    BackupSet = "${var.environment}-projects"
  }

  depends_on = [aws_iam_role_policy.project_backup_creation]
}

# The policy ID scopes cleanup without creating a role/policy dependency cycle.
resource "aws_iam_role_policy" "project_backup_lifecycle" {
  name = "${local.backup_name}-lifecycle"
  role = aws_iam_role.project_backups.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ManagePolicySnapshots"
      Effect   = "Allow"
      Action   = ["ec2:CreateTags", "ec2:DeleteSnapshot"]
      Resource = local.backup_snapshot_arn
      Condition = {
        StringEquals = {
          "ec2:ResourceTag/aws:dlm:lifecycle-policy-id" = aws_dlm_lifecycle_policy.projects.id
        }
      }
    }]
  })
}
