# Development host infrastructure guidance

Source-Template-Version: 1.0.0
Template-Source: GptClaw templates/agents/nested/AGENTS.md.template

## Scope and ownership

Area-Scope: infra/dev-host
Parent-Guidance: ../../AGENTS.md
Owner: Daniel

This subtree owns the development host's Terraform, cloud-init, and Terraform
tests. Follow the [repository contract](../../AGENTS.md) and active initiative
from the [documentation index](../../docs/README.md). These local details apply
only to this subtree; inspect deeper guidance before work there.

## Local conventions

Use [.terraform-version](.terraform-version), [versions.tf](versions.tf), and
[the provider lock](.terraform.lock.hcl) as version sources. Preserve immutable
bootstrap pins and review cloud-init changes as host replacement changes:
[compute.tf](compute.tf) enables replacement on user-data changes. Do not turn
architecture proposals into installed tools or additional resources.

Use synthetic values in [tests](tests). Inspect provider declarations in each
changed test: AWS is mocked, but [host-policy tests](tests/host-policy.tftest.hcl)
use the real local cloud-init provider. A mock label does not establish that
all providers or operations are mocked.

## Commands and verification

Use the exact commands, working directories, prerequisites, and side effects
in the [root command table](../../AGENTS.md#commands-and-quality-gates), grounded
in [README](../../README.md) and [CI](../../.github/workflows/terraform-dev-host.yml).
Select checks by the actual change:

- Documentation: diff and relative-link review.
- Policy or template changes: repository checks, which use isolated fixtures;
  they do not install the host policy.
- Terraform behavior: repository checks and the root table's Terraform format,
  backend-free initialization when needed, validation, and tests. Initialization
  needs network access and writes local provider data; inspect tests first.

Run Terraform commands from `infra/dev-host`, repository scripts from the root.
Use the pinned tool; do not install host packages to make verification pass.
There is no application startup or build target in this area. Report local,
CI, deployed, and acceptance results separately, including skipped checks.

## Constraints

Keep infrastructure mutations on committed code -> GitHub Actions -> HCP
Terraform -> AWS. Plans and applies use the protected workflow; no local apply
or direct AWS mutation. Preserve project-volume/identity deletion protection,
private access, and development/production separation. State, saved plans,
variable files, credentials, and runtime data are not fixtures or commit evidence.

Respect higher-priority instructions, prior session authorization, and actual
permissions. This file grants no new authority and does not enforce a security
boundary. Report unresolved conflicts and continue unaffected authorized work.
Do not repeat approval questions for already-authorized scope.

## Maintenance

Daniel owns this adaptation of nested template 1.0.0. Follow the
[area adaptation/update/rollback guide](../../templates/agents/nested/README.md).
Keep it within 4 KiB UTF-8. Adopt later changes deliberately in a reviewed PR;
version equality is provenance, not synchronization. Revert targeted changes
while preserving unrelated work, and verify restored guidance in a fresh task.
Do not install host policy, alter global settings, or reload ongoing tasks.
