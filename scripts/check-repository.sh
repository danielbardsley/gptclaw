#!/usr/bin/env bash
set -Eeuo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

status=0

if grep -RInE --include='*.yml' --include='*.yaml' \
  '^[[:space:]]*uses:[[:space:]]+[^#[:space:]]+@(main|master|v[0-9]+)([[:space:]#]|$)' \
  .github; then
  echo "GitHub Actions must be pinned to full immutable commit SHAs." >&2
  status=1
fi

if git grep -InE \
  '(AKIA[0-9A-Z]{16}|-----BEGIN ([A-Z0-9 ]+ )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|tskey-(auth|api)-[A-Za-z0-9-]{10,})' \
  -- ':!scripts/check-repository.sh'; then
  echo "A value resembling a credential was found in tracked source." >&2
  status=1
fi

if git ls-files | grep -E '(^|/)(terraform\.tfstate($|\.)|[^/]+\.tfplan$|\.env($|\.)|auth\.json$)'; then
  echo "A generated state, plan, environment, or authentication file is tracked." >&2
  status=1
fi

if grep -RInE '^[[:space:]]*ingress[[:space:]]*\{' infra/dev-host --include='*.tf'; then
  echo "Inline security-group ingress is forbidden for the development host." >&2
  status=1
fi

if ! grep -Eq '^[[:space:]]*prevent_destroy[[:space:]]*=[[:space:]]*true' infra/dev-host/storage.tf; then
  echo "The persistent project volume must retain prevent_destroy = true." >&2
  status=1
fi

if ! grep -Eq '^[[:space:]]*prevent_destroy[[:space:]]*=[[:space:]]*true' infra/dev-host/hcp_identity.tf; then
  echo "The HCP OIDC provider and deployment roles must be protected from accidental destruction." >&2
  status=1
fi

if ! grep -Eq '^[[:space:]]*secret_string_wo[[:space:]]*=' infra/dev-host/secrets.tf; then
  echo "The Tailscale auth key must use the provider's write-only secret argument." >&2
  status=1
fi

if grep -Eq '^[[:space:]]*secret_string[[:space:]]*=' infra/dev-host/secrets.tf; then
  echo "The Tailscale auth key must never use the state-persisted secret_string argument." >&2
  status=1
fi

hcp_self_management=$(sed -n '/sid[[:space:]]*=[[:space:]]*"ManageDevelopmentHostRole"/,/^[[:space:]]*}/p' infra/dev-host/hcp_identity.tf)
if grep -q 'hcp-apply' <<<"$hcp_self_management"; then
  echo "The dynamic apply role must not be allowed to modify its own permissions." >&2
  status=1
fi

if ! grep -Eq '^[[:space:]]*user_data_replace_on_change[[:space:]]*=[[:space:]]*true' infra/dev-host/compute.tf; then
  echo "Bootstrap changes must trigger a reviewed compute replacement." >&2
  status=1
fi

if grep -Eq '^[[:space:]]*key_name[[:space:]]*=' infra/dev-host/compute.tf; then
  echo "The development host must not use an EC2 key pair." >&2
  status=1
fi

if ! grep -Eq '^[[:space:]]*tags[[:space:]]*=[[:space:]]*local\.common_tags' infra/dev-host/providers.tf; then
  echo "The AWS provider must apply the common traceability tags." >&2
  status=1
fi

if ! ./scripts/install-host-agents.sh validate-source; then
  status=1
fi

if ! ./scripts/tests/install-host-agents.sh; then
  status=1
fi

if ! python3 ./scripts/tests/test_host_policy_bootstrap.py; then
  status=1
fi

exit "$status"
