variable "aws_account_id" {
  description = "Twelve-digit AWS account ID approved for the development host."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "aws_account_id must contain exactly 12 digits."
  }
}

variable "aws_region" {
  description = "AWS region approved for the development host."
  type        = string

  validation {
    condition     = can(regex("^[a-z]{2}(-gov)?-[a-z]+-[0-9]$", var.aws_region))
    error_message = "aws_region must be a valid AWS region name."
  }
}

variable "availability_zone" {
  description = "Sticky availability zone for both compute and persistent project storage."
  type        = string

  validation {
    condition     = startswith(var.availability_zone, var.aws_region) && length(var.availability_zone) > length(var.aws_region)
    error_message = "availability_zone must belong to aws_region."
  }
}

variable "project_name" {
  description = "Lowercase project identifier used in resource names."
  type        = string
  default     = "gptclaw"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}[a-z0-9]$", var.project_name))
    error_message = "project_name must be a lowercase, naming-safe identifier."
  }
}

variable "environment" {
  description = "Deployment environment. This root module is development-only."
  type        = string
  default     = "development"

  validation {
    condition     = var.environment == "development"
    error_message = "Only the development environment is allowed by this root module."
  }
}

variable "instance_name" {
  description = "Hostname and Name tag for the remote development host."
  type        = string
  default     = "forge-dev-01"

  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", var.instance_name))
    error_message = "instance_name must be a valid lowercase hostname."
  }
}

variable "instance_type" {
  description = "Allowlisted EC2 instance type."
  type        = string
  default     = "t3.large"

  validation {
    condition     = contains(["t3.medium", "t3.large", "t3.xlarge", "t3.2xlarge"], var.instance_type)
    error_message = "instance_type must be one of the approved T3 general-purpose sizes."
  }
}

variable "vpc_cidr" {
  description = "RFC1918 CIDR for the dedicated development VPC."
  type        = string
  default     = "10.42.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr)) && startswith(var.vpc_cidr, "10.") && endswith(var.vpc_cidr, "/16")
    error_message = "vpc_cidr must be a valid /16 CIDR within 10.0.0.0/8."
  }
}

variable "subnet_cidr" {
  description = "CIDR for the single development subnet."
  type        = string
  default     = "10.42.10.0/24"

  validation {
    condition = (
      can(cidrnetmask(var.subnet_cidr)) &&
      endswith(var.subnet_cidr, "/24") &&
      contains([for subnet_number in range(256) : cidrsubnet(var.vpc_cidr, 8, subnet_number)], var.subnet_cidr)
    )
    error_message = "subnet_cidr must be a canonical /24 subnet contained by vpc_cidr."
  }
}

variable "root_volume_size_gib" {
  description = "Encrypted root-volume size in GiB."
  type        = number
  default     = 30

  validation {
    condition     = var.root_volume_size_gib >= 20
    error_message = "root_volume_size_gib must be at least 20 GiB."
  }
}

variable "data_volume_size_gib" {
  description = "Persistent encrypted project-volume size in GiB. Never shrink this value."
  type        = number
  default     = 80

  validation {
    condition     = var.data_volume_size_gib >= 40
    error_message = "data_volume_size_gib must be at least 40 GiB."
  }
}

variable "desktop_ssh_public_key" {
  description = "Public half of the dedicated desktop-to-host SSH key."
  type        = string

  validation {
    condition = (
      can(regex("^(ssh-ed25519|ecdsa-sha2-nistp256|ssh-rsa) [A-Za-z0-9+/=]+(?: .*)?$", trimspace(var.desktop_ssh_public_key))) &&
      !strcontains(upper(var.desktop_ssh_public_key), "PRIVATE KEY")
    )
    error_message = "desktop_ssh_public_key must be one valid public SSH key and must not contain private-key material."
  }
}

variable "tailscale_auth_key" {
  description = "Fresh one-use, tagged Tailscale auth key. HCP Terraform supplies it ephemerally and Terraform never stores it in state."
  type        = string
  sensitive   = true
  ephemeral   = true

  validation {
    condition     = can(regex("^tskey-auth-", var.tailscale_auth_key))
    error_message = "tailscale_auth_key must be a Tailscale authentication key."
  }
}

variable "tailscale_auth_key_version" {
  description = "Monotonic version used to rotate the write-only Tailscale secret value. Increment whenever tailscale_auth_key changes."
  type        = number
  default     = 1

  validation {
    condition     = var.tailscale_auth_key_version >= 1 && floor(var.tailscale_auth_key_version) == var.tailscale_auth_key_version
    error_message = "tailscale_auth_key_version must be a positive integer."
  }
}

variable "hcp_terraform_organization" {
  description = "HCP Terraform organization trusted to assume the AWS deployment roles."
  type        = string
  default     = "Bardsley"
}

variable "hcp_terraform_project" {
  description = "HCP Terraform project trusted to assume the AWS deployment roles."
  type        = string
  default     = "gptclaw"
}

variable "hcp_terraform_workspace" {
  description = "HCP Terraform workspace trusted to assume the AWS deployment roles."
  type        = string
  default     = "gptclaw-dev-host"
}

variable "tailscale_tag" {
  description = "Tailscale ACL tag advertised by the development host."
  type        = string
  default     = "tag:gptclaw-dev"

  validation {
    condition     = can(regex("^tag:[a-zA-Z0-9-]+$", var.tailscale_tag))
    error_message = "tailscale_tag must begin with tag: and contain only letters, digits, and hyphens."
  }
}

variable "deployment_revision" {
  description = "Exact Git commit SHA that initiated the deployment."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{40}$", var.deployment_revision))
    error_message = "deployment_revision must be a full lowercase 40-character Git SHA."
  }
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365], var.log_retention_days)
    error_message = "log_retention_days must be a supported CloudWatch Logs retention value."
  }
}
