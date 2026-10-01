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

# Preserve the existing value; stop managing it without deleting its version.
# The protected secret container remains for deliberate later retirement.
removed {
  from = aws_secretsmanager_secret_version.tailscale_enrollment
  lifecycle { destroy = false }
}
