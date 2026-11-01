variable "android_runner_state" {
  description = "Explicit state of the separate private Android runner; workflow defaults to stopped."
  type        = string
  default     = "stopped"

  validation {
    condition     = contains(["running", "stopped"], var.android_runner_state)
    error_message = "android_runner_state must be running or stopped."
  }
}

data "cloudinit_config" "android_runner" {
  gzip          = true
  base64_encode = true

  part {
    content_type = "text/cloud-config"
    content = templatefile("${path.module}/templates/android-runner.yaml.tftpl", {
      desktop_ssh_public_key      = trimspace(var.desktop_ssh_public_key)
      runner_ssh_public_key       = trimspace(file("${path.module}/android-runner.pub"))
      tailscale_federation_helper = file("${path.module}/lib/tailscale_federation.py")
      federation_config = jsonencode({
        client_id = var.tailscale_federation_client_id
        audience  = local.tailscale_federation_audience
        tag       = var.tailscale_tag
        hostname  = "forge-android-01"
        region    = var.aws_region
      })
      android_setup = file("${path.module}/lib/android_runner.py")
      android_pins  = file("${path.module}/android-runner-artifacts.json")
    })
  }
}

resource "aws_instance" "android_runner" {
  ami                                  = data.aws_ssm_parameter.ubuntu_ami.value
  instance_type                        = "m7i.xlarge"
  availability_zone                    = var.availability_zone
  subnet_id                            = aws_subnet.dev_public.id
  vpc_security_group_ids               = [aws_security_group.dev_host.id]
  associate_public_ip_address          = true
  iam_instance_profile                 = aws_iam_instance_profile.dev_host.name
  user_data_base64                     = data.cloudinit_config.android_runner.rendered
  user_data_replace_on_change          = true
  instance_initiated_shutdown_behavior = "stop"

  cpu_options {
    nested_virtualization = "enabled"
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }

  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    volume_size           = 80
    delete_on_termination = true
    tags                  = { Name = "${local.name_prefix}-android-root" }
  }

  tags = {
    Name    = "forge-android-01"
    Purpose = "Private Android emulator; synthetic test data only"
  }

  lifecycle {
    prevent_destroy = true
    # EC2 releases an auto-assigned public IP while stopped. The pinned provider
    # reads that temporary absence as false, although this creation setting is
    # ForceNew. Keep the existing instance/disk for ordinary protected restarts.
    ignore_changes = [ami, user_data_base64, associate_public_ip_address]
    precondition {
      condition     = var.aws_region == "us-east-1"
      error_message = "The existing federation helper is reviewed only for us-east-1."
    }
  }

  depends_on = [aws_iam_role_policy_attachment.ssm, aws_iam_role_policy.dev_host_runtime]
}

resource "aws_ec2_instance_state" "android_runner" {
  instance_id = aws_instance.android_runner.id
  state       = var.android_runner_state
}

output "android_runner" {
  description = "Private test appliance; bootstrap and Android readiness require live verification."
  value = {
    instance_id        = aws_instance.android_runner.id
    tailscale_hostname = "forge-android-01"
    requested_state    = var.android_runner_state
    automatic_stop     = "4 hours after boot"
  }
}
