# SPEC-015 acceptance evidence

- **Status:** Local implementation and CI verified; deployed acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-01 (America/New_York)
- **Implementation revision:** `fd1d1d3d708469f74775a959f620bc9e8a8447f2`
- **Review:** [PR #25](https://github.com/danielbardsley/gptclaw/pull/25), merged as `c4c273c8aae5c2ff848576ab7d294b49d2017c94`
- **Plans:** [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)

## Authorization and source disposition

Daniel authorized implementation with “Implement SYS-004” and approved temporary
exceptions for the five existing upstream channels through November 1, 2026.
The profile records owner Daniel, component scope, reason, approval/expiry dates
and removal steps. Expiry uses America/New_York dates and blocks new provisioning
from November 2. Replacement by reviewed versioned sources requires owner
follow-through; this feature does not schedule an updater or stop installed tools.

Read-only discovery confirmed Ubuntu 24.04 amd64, Python 3.12.3, `forge` without
additional groups, the existing baseline apt package versions, CloudWatch's
installed package and the SSM stable snap. Only named package/identity metadata
was read. This was not a complete installed receipt or deployed acceptance.
The repository's existing upstream source mechanisms were retained under the
approved exceptions; SYS-001 installs no tools in this implementation.

## Criterion mapping

| Criterion | State | Evidence or limitation | Remaining action/owner |
|---|---|---|---|
| AC-001 | passed | Strict parser/schema tests reject malformed/duplicate/unsafe declarations before installer calls. Profile accounts for all 12 explicit apt packages and five existing component adapters. | Review implementation PR, Daniel. |
| AC-002 | passed | Offline version/source and checksum-failure tests pass without fallback. Five channel exceptions explicitly approved by Daniel; exact archive verification exercised with synthetic bytes. | Replace exceptions before expiry, Daniel and implementer. |
| AC-003 | passed | Mock-AWS/real-cloud-init tests verify embedded profile/helper bytes and deployment revision, ordering, size and replacement wiring; no new privileges or independent installer list. | Protected deployment remains separate. |
| AC-004 | pending | Local stale/partial receipt, interrupted write and failed final probe tests pass. No replacement host receipt has been produced. | Compare deployed receipt/provenance and verify tools, operator. |
| AC-005 | passed | Repeat/conflict/retirement fixtures preserve unrelated state and avoid uninstall calls. Required bootstrap consumers explicitly gate retirement. | Review operational migration before deployment, Daniel. |
| AC-006 | pending | Recovery runbook and availability/expiry limitations documented; no protected plan, apply, replacement or rollback drill was run. | Review recovery point/window, authorize deployment and verify data/access, Daniel/operator. |
| AC-007 | pending | Runbook, local evidence and successful CI reference exist; deployment and final owner acceptance remain separate. | Review CI, merge, deployed results and acceptance, Daniel. |

“Passed” above describes the criterion's local evidence only; it does not mark
SYS-004 Delivered. Required host checks and final acceptance remain pending.

## Executed verification

Local environment: unprivileged `forge`, Python 3.12.3, existing isolated manifest
dependencies at `/tmp/gptclaw-prj001-venv`, existing pinned Terraform 1.16.1 at
`/tmp/gptclaw-res001-tools/terraform`, and already initialized locked providers.
No package installation or provider reinitialization was needed.

| Command | Result |
|---|---|
| `source /tmp/gptclaw-prj001-venv/bin/activate && ./scripts/check-repository.sh` | Passed all repository checks, including 19 focused host-tool tests. Installers/network/systemd were mocked in those tests. |
| `python3 -B infra/dev-host/lib/host_tools.py validate infra/dev-host/host-tools.json` | Passed; canonical profile SHA-256 `20ae220be10f3e70a42b440a4ec7c20a4cce2c28efad2d2fa539230fc2c195a3`. |
| `bash -n scripts/check-repository.sh` | Passed. |
| `bash -n infra/dev-host/templates/bootstrap-forge.sh.tftpl` | Passed. |
| Terraform 1.16.1 `fmt -check -recursive` and `validate -no-color`, from `infra/dev-host` | Passed. |
| Terraform 1.16.1 `test -no-color`, from `infra/dev-host` | Final full run: 19 passed, zero failed; AWS mocked, cloud-init local. |
| Terraform 1.16.1 `test -no-color -filter=tests/host-tools.tftest.hcl -filter=tests/host-policy.tftest.hcl` | Final targeted run: four passed, including added byte-for-byte YAML embedding assertion. |
| `git diff --check` and `git diff --cached --check` | Passed after removing one trailing blank line caught when staging the new Terraform test. |

An intermediate Terraform run failed two payload-size assertions after helper
expansion (base64 lengths 21852/21856 versus limit 21844). The fix uses YAML literal
content for the new profile/helper inside the existing compressed cloud-init
payload, avoiding redundant base64 expansion. The size gate was not weakened;
both the full rerun and final targeted tests passed. No infrastructure was touched.

## Remaining delivery work

GitHub Actions [run 36815940238](https://github.com/danielbardsley/gptclaw/actions/runs/36815940238)
completed successfully for `12c98c3d0b14468050802fb704e97244a7698e21`, which contains
implementation `fd1d1d3` plus this evidence record. This was the pull-request quality
workflow, not a protected plan/apply. The subsequent change recording this CI
result is documentation-only; CI evidence here refers to that exact tested SHA.
Daniel authorized and completed the PR merge on October 1, 2026. No deployment
was performed. The PR also contains the previously requested SYS-001 planning documents, which
remain unimplemented. Before any replacement, obtain Daniel's concrete deployment
authorization and follow [Manage host tools](../../runbooks/manage-host-tools.md)
and [host recovery](../../runbooks/recover-dev-host.md). Confirm a suitable recovery
point, review protected resource retention, quiesce writes and record the window.

After authorized deployment, verify private access, project filesystem UUID and
ownership, all required tool versions, matching profile digest/revision and absence
of stale success. Record actual deployment/run links and Daniel's acceptance.
Rollback is documented but unexecuted. No local install, Terraform apply, direct
AWS mutation, merge, deployed tool verification or final acceptance is claimed.

## AWS CLI accessibility repair — October 8, 2026

Daniel authorized code, PR merge, protected re-plan and replacement, retaining
backup/recovery requirements and all EC2 configuration through IaC. The current
root-owned AWS installation has mode 750 and is inaccessible to forge. No live
permissions were changed. The bootstrap installer now uses a child-only umask
of 022; final receipt verification requires the same AWS CLI version as forge.
Twenty-one focused offline tests passed, including a real synthetic subprocess
permission regression, unchanged parent umask, denied user execution and version
mismatch. This does not establish deployed CLI usability.

Full offline repository checks passed after the final extraction/installer
umask change. Terraform 1.16.5 format/validate and all 24 development-root tests
passed before the extraction adjustment; the affected host-tool rendering test
is rerun against the final helper. Whitespace and relative links passed.
