terraform {
  required_version = "= 1.16.5"
  cloud {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.62"
    }
  }
}

variable "aws_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "A reviewed 12-digit AWS account ID is required."
  }
}

variable "adopt_existing_issuer" {
  description = "Only true after confirming the account issuer exists and is not owned by another Terraform state."
  type        = bool
  default     = false
}

provider "aws" {
  region              = "us-east-1"
  allowed_account_ids = [var.aws_account_id]
}

# Account-wide prerequisite; never grant this administration to the host or its
# normal HCP apply role. Deletion would break every consumer of the account issuer.
resource "aws_iam_outbound_web_identity_federation" "tailscale" {
  lifecycle { prevent_destroy = true }
}

import {
  for_each = var.adopt_existing_issuer ? toset([var.aws_account_id]) : toset([])
  to       = aws_iam_outbound_web_identity_federation.tailscale
  id       = each.value
}

output "issuer_url" {
  value = aws_iam_outbound_web_identity_federation.tailscale.issuer_identifier
}

output "tailscale_subject" {
  value = "arn:aws:iam::${var.aws_account_id}:role/gptclaw-dev-host"
}
