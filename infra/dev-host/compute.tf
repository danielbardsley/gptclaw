locals {
  host_policy_script = templatefile("${path.module}/templates/install-host-policy.sh.tftpl", {
    host_policy_revision = var.host_policy_revision
  })

  bootstrap_script = templatefile("${path.module}/templates/bootstrap-forge.sh.tftpl", {
    aws_region                 = var.aws_region
    data_volume_id             = aws_ebs_volume.projects.id
    instance_name              = var.instance_name
    log_group_name             = aws_cloudwatch_log_group.dev_host.name
    tailscale_auth_secret_arn  = aws_secretsmanager_secret.tailscale_enrollment.arn
    tailscale_auth_key_version = var.tailscale_auth_key_version
    tailscale_tag              = var.tailscale_tag
  })
}

data "cloudinit_config" "dev_host" {
  gzip          = true
  base64_encode = true

  part {
    content_type = "text/cloud-config"
    filename     = "cloud-init.yaml"
    content = templatefile("${path.module}/templates/cloud-init.yaml.tftpl", {
      bootstrap_script       = local.bootstrap_script
      host_policy_script     = local.host_policy_script
      desktop_ssh_public_key = trimspace(var.desktop_ssh_public_key)
      instance_name          = var.instance_name
    })
  }
}

resource "aws_instance" "dev_host" {
  ami                                  = data.aws_ssm_parameter.ubuntu_ami.value
  instance_type                        = var.instance_type
  availability_zone                    = var.availability_zone
  subnet_id                            = aws_subnet.dev_public.id
  vpc_security_group_ids               = [aws_security_group.dev_host.id]
  associate_public_ip_address          = true
  iam_instance_profile                 = aws_iam_instance_profile.dev_host.name
  user_data_base64                     = data.cloudinit_config.dev_host.rendered
  user_data_replace_on_change          = true
  instance_initiated_shutdown_behavior = "stop"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }

  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    volume_size           = var.root_volume_size_gib
    delete_on_termination = true

    tags = merge(local.common_tags, {
      Name = "${local.name_prefix}-root"
    })
  }

  tags = {
    Name = var.instance_name
  }

  depends_on = [
    aws_iam_role_policy_attachment.ssm,
    aws_iam_role_policy.dev_host_runtime,
  ]
}
