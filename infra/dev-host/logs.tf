resource "aws_cloudwatch_log_group" "dev_host" {
  name              = "/${var.project_name}/${var.environment}/${var.instance_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${local.name_prefix}-host"
  }
}
