mock_provider "aws" {
  mock_resource "aws_iam_outbound_web_identity_federation" {
    defaults = { issuer_identifier = "https://synthetic.tokens.sts.global.api.aws" }
  }
}
variables { aws_account_id = "123456789012" }
run "account_issuer" {
  command = apply
  assert {
    condition     = output.issuer_url == "https://synthetic.tokens.sts.global.api.aws" && output.tailscale_subject == "arn:aws:iam::123456789012:role/gptclaw-dev-host"
    error_message = "Setup must expose only the account issuer and exact development role subject."
  }
}
run "invalid_account" {
  command = plan
  variables { aws_account_id = "invalid" }
  expect_failures = [var.aws_account_id]
}
