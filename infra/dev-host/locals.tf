locals {
  name_prefix = "${var.project_name}-dev"

  common_tags = {
    Project            = "GptClaw"
    Environment        = var.environment
    ManagedBy          = "Terraform"
    Repository         = "danielbardsley/gptclaw"
    TerraformWorkspace = "gptclaw-dev-host"
    Owner              = "Daniel"
    DeploymentRevision = var.deployment_revision
  }
}
