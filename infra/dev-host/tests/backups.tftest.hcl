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
  mock_resource "aws_ebs_volume" {
    defaults = { id = "vol-0123456789abcdef0" }
  }
  mock_resource "aws_dlm_lifecycle_policy" {
    defaults = {
      id  = "policy-0123456789abcdef0"
      arn = "arn:aws:dlm:us-east-1:123456789012:policy/policy-0123456789abcdef0"
    }
  }
}
mock_provider "cloudinit" {}

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

run "snapshot_defaults_and_boundaries" {
  command = apply

  assert {
    condition = (
      aws_dlm_lifecycle_policy.projects.state == "ENABLED" &&
      one(aws_dlm_lifecycle_policy.projects.policy_details).policy_type == "EBS_SNAPSHOT_MANAGEMENT" &&
      toset(one(aws_dlm_lifecycle_policy.projects.policy_details).resource_types) == toset(["VOLUME"]) &&
      one(aws_dlm_lifecycle_policy.projects.policy_details).target_tags == tomap({ GptClawBackup = "development-projects" }) &&
      aws_ebs_volume.projects.tags.GptClawBackup == "development-projects" &&
      !contains(keys(local.common_tags), "GptClawBackup") &&
      !contains(keys(aws_instance.dev_host.tags), "GptClawBackup")
    )
    error_message = "Only the explicitly tagged project volume may be selected, never the whole instance or common-tagged resources."
  }
  assert {
    condition = (
      length(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule) == 1 &&
      one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).interval == 24 &&
      one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).interval_unit == "HOURS" &&
      toset(one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).times) == toset(["03:00"]) &&
      one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).retain_rule).count == 7
    )
    error_message = "The default is one daily 03:00 UTC schedule retaining seven snapshots."
  }
  assert {
    condition = (
      !one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).copy_tags &&
      toset(keys(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).tags_to_add)) ==
      toset(["Project", "Environment", "Repository", "BackupSet", "RetentionClass"]) &&
      length(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).share_rule) == 0 &&
      length(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).cross_region_copy_rule) == 0 &&
      length(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).fast_restore_rule) == 0 &&
      length(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).archive_rule) == 0 &&
      length(one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).scripts) == 0
    )
    error_message = "Snapshots must use only allowlisted metadata with no sharing, copying, archiving, fast restore, or scripts."
  }
  assert {
    condition = (
      aws_ebs_volume.projects.encrypted &&
      aws_volume_attachment.projects.volume_id == aws_ebs_volume.projects.id &&
      !aws_volume_attachment.projects.force_detach &&
      length(aws_security_group.dev_host.ingress) == 0 &&
      !strcontains(aws_iam_role_policy.dev_host_runtime.policy, "Snapshot")
    )
    error_message = "Backups must preserve the volume, attachment, ingress boundary, and unprivileged host role."
  }
  assert {
    condition = (
      one(jsondecode(aws_iam_role.project_backups.assume_role_policy).Statement).Principal.Service == "dlm.amazonaws.com" &&
      one(jsondecode(aws_iam_role.project_backups.assume_role_policy).Statement).Condition.StringEquals["aws:SourceAccount"] == "123456789012" &&
      one(jsondecode(aws_iam_role.project_backups.assume_role_policy).Statement).Condition.ArnLike["aws:SourceArn"] == "arn:aws:dlm:us-east-1:123456789012:policy/*"
    )
    error_message = "Only DLM policies in the approved account and Region can assume the backup role."
  }
  assert {
    condition = (
      one([for s in jsondecode(aws_iam_role_policy.project_backup_creation.policy).Statement :
        s.Resource if s.Sid == "SnapshotProjectVolume"
      ]) == "arn:aws:ec2:us-east-1:123456789012:volume/vol-0123456789abcdef0" &&
      alltrue([for s in jsondecode(aws_iam_role_policy.project_backup_creation.policy).Statement :
        s.Resource != "*" || s.Sid == "DiscoverSnapshotMetadata"
      ]) &&
      one([for s in jsondecode(aws_iam_role_policy.project_backup_creation.policy).Statement :
        s.Condition.StringEquals["ec2:CreateAction"] if s.Sid == "TagSnapshotAtCreation"
      ]) == "CreateSnapshot"
    )
    error_message = "Snapshot creation must be limited to the exact source volume; tagging new snapshots requires create context."
  }
  assert {
    condition = (
      one(jsondecode(aws_iam_role_policy.project_backup_lifecycle.policy).Statement).Resource == "arn:aws:ec2:us-east-1::snapshot/*" &&
      one(jsondecode(aws_iam_role_policy.project_backup_lifecycle.policy).Statement).Condition.StringEquals["ec2:ResourceTag/aws:dlm:lifecycle-policy-id"] == aws_dlm_lifecycle_policy.projects.id &&
      toset(one(jsondecode(aws_iam_role_policy.project_backup_lifecycle.policy).Statement).Action) == toset(["ec2:CreateTags", "ec2:DeleteSnapshot"])
    )
    error_message = "Existing-snapshot tagging and deletion require this exact policy's attribution."
  }
  assert {
    condition = alltrue([
      for s in concat(
        jsondecode(aws_iam_role_policy.project_backup_creation.policy).Statement,
        jsondecode(aws_iam_role_policy.project_backup_lifecycle.policy).Statement
        ) : alltrue([for action in flatten([s.Action]) :
          contains(["ec2:DescribeVolumes", "ec2:DescribeSnapshots", "ec2:CreateSnapshot", "ec2:CreateTags", "ec2:DeleteSnapshot"], action)
      ])
    ])
    error_message = "DLM must not gain host, sharing, notification, KMS administration, or unrelated mutation permissions."
  }
  assert {
    condition = (
      output.project_backup.policy_id == aws_dlm_lifecycle_policy.projects.id &&
      output.project_backup.volume_id == aws_ebs_volume.projects.id &&
      output.project_backup.retention_count == 7
    )
    error_message = "Discovery must expose current Terraform resource identities and retention, not historical IDs."
  }
}

run "reviewed_overrides_and_disable" {
  command = plan
  variables {
    backup_policy_enabled  = false
    backup_interval_hours  = 12
    backup_start_time_utc  = "23:59"
    backup_retention_count = 1
  }
  assert {
    condition = (
      aws_dlm_lifecycle_policy.projects.state == "DISABLED" &&
      one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).interval == 12 &&
      contains(one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).create_rule).times, "23:59") &&
      one(one(one(aws_dlm_lifecycle_policy.projects.policy_details).schedule).retain_rule).count == 1 &&
      aws_ebs_volume.projects.tags.GptClawBackup == "development-projects"
    )
    error_message = "Reviewed overrides must alter policy settings without removing the persistent volume's selection tag."
  }
}

run "reject_unsupported_interval" {
  command = plan
  variables { backup_interval_hours = 6 }
  expect_failures = [var.backup_interval_hours]
}
run "reject_zero_retention" {
  command = plan
  variables { backup_retention_count = 0 }
  expect_failures = [var.backup_retention_count]
}
run "reject_fractional_retention" {
  command = plan
  variables { backup_retention_count = 1.5 }
  expect_failures = [var.backup_retention_count]
}
run "reject_excessive_retention" {
  command = plan
  variables { backup_retention_count = 1001 }
  expect_failures = [var.backup_retention_count]
}
run "reject_invalid_hour" {
  command = plan
  variables { backup_start_time_utc = "24:00" }
  expect_failures = [var.backup_start_time_utc]
}
run "reject_invalid_minute" {
  command = plan
  variables { backup_start_time_utc = "03:60" }
  expect_failures = [var.backup_start_time_utc]
}
run "reject_noncanonical_time" {
  command = plan
  variables { backup_start_time_utc = "3:00" }
  expect_failures = [var.backup_start_time_utc]
}
