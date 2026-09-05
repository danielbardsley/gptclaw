resource "aws_secretsmanager_secret" "tailscale_enrollment" {
  name                    = "${var.project_name}/${var.environment}/tailscale-enrollment"
  description             = "One-use Tailscale enrollment key for ${var.instance_name}"
  recovery_window_in_days = 30

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "${local.name_prefix}-tailscale-enrollment"
  }
}

resource "aws_secretsmanager_secret_version" "tailscale_enrollment" {
  secret_id                = aws_secretsmanager_secret.tailscale_enrollment.id
  secret_string_wo         = var.tailscale_auth_key
  secret_string_wo_version = var.tailscale_auth_key_version
}
