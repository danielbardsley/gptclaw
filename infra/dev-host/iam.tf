resource "aws_iam_role" "dev_host" {
  name = "${local.name_prefix}-host"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.${data.aws_partition.current.dns_suffix}" }
    }]
  })

  tags = {
    Name = "${local.name_prefix}-host"
  }
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.dev_host.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "dev_host_runtime" {
  name = "${local.name_prefix}-host-runtime"
  role = aws_iam_role.dev_host.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "DiscoverHostLogGroup"
        Effect   = "Allow"
        Action   = ["logs:DescribeLogGroups"]
        Resource = "*"
      },
      {
        Sid    = "WriteHostLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
        ]
        Resource = "${aws_cloudwatch_log_group.dev_host.arn}:*"
      },
      {
        Sid    = "ReadTailscaleEnrollmentSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
        ]
        Resource = var.tailscale_auth_secret_arn
      },
    ]
  })
}

resource "aws_iam_instance_profile" "dev_host" {
  name = "${local.name_prefix}-host"
  role = aws_iam_role.dev_host.name

  tags = {
    Name = "${local.name_prefix}-host"
  }
}
