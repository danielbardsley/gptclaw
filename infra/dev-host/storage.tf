resource "aws_ebs_volume" "projects" {
  availability_zone = var.availability_zone
  size              = var.data_volume_size_gib
  type              = "gp3"
  encrypted         = true

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "${local.name_prefix}-projects"
  }
}

resource "aws_volume_attachment" "projects" {
  device_name  = "/dev/sdf"
  volume_id    = aws_ebs_volume.projects.id
  instance_id  = aws_instance.dev_host.id
  force_detach = false
}
