output "instance_id" {
  description = "EC2 instance ID for Systems Manager and diagnostics."
  value       = aws_instance.dev_host.id
}

output "availability_zone" {
  description = "Sticky availability zone containing compute and project storage."
  value       = var.availability_zone
}

output "data_volume_id" {
  description = "Persistent encrypted EBS volume containing project data."
  value       = aws_ebs_volume.projects.id
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group receiving host bootstrap and authentication logs."
  value       = aws_cloudwatch_log_group.dev_host.name
}

output "ssm_start_session_command" {
  description = "Break-glass command for an authorized AWS operator."
  value       = "aws ssm start-session --region ${var.aws_region} --target ${aws_instance.dev_host.id}"
}

output "expected_tailscale_hostname" {
  description = "Hostname the instance advertises to Tailscale."
  value       = var.instance_name
}

output "deployment_revision" {
  description = "Git revision associated with the deployment."
  value       = var.deployment_revision
}

output "hcp_terraform_plan_role_arn" {
  description = "AWS role configured as TFC_AWS_PLAN_ROLE_ARN after the bootstrap apply."
  value       = aws_iam_role.hcp_plan.arn
}

output "hcp_terraform_apply_role_arn" {
  description = "AWS role configured as TFC_AWS_APPLY_ROLE_ARN after the bootstrap apply."
  value       = aws_iam_role.hcp_apply.arn
}

output "tailscale_enrollment_secret_arn" {
  description = "Secrets Manager ARN used once by the host to join Tailscale."
  value       = aws_secretsmanager_secret.tailscale_enrollment.arn
}
