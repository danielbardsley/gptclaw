# SPEC-021 acceptance evidence

- **Status:** In review — local/live checks passed; CI/review, final owner acceptance and merge pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-021](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **Operation:** [Template runbook](../../runbooks/manage-project-templates.md)
- **Implementation PR:** [PR #50](https://github.com/danielbardsley/gptclaw/pull/50)
- **Baseline:** main `7cb0c878a10849510f7985eb052b7509297c7ccc`
- **Provider:** 1.3.0; template catalogue schema 1; runtime/dependency/toolchain receipt schemas unchanged

Daniel authorized implementation with “Ok, now implement the spec”. These checks
use synthetic app sources and the unprivileged forge identity. No AWS, host package,
policy installer, credential, public exposure or production change ran.

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed locally/live | Deterministic source and installed list/show JSON agree; observation-only tests guard calls/writes and file inventory. Unknown/ranged/partial selections fail without fallback. |
| AC-002 | passed locally | Strict schema/path/type/duplicate/integrity/compatibility fixtures reject before destination creation. Git baseline fixture rejects historical descriptor mutation even with recomputed digest. CI baseline comparison is configured; remote outcome pending. |
| AC-003 | passed locally/live | Default/exact generation, distinct synthetic release bytes, normalized reproducibility and release-selected toolchain independent of registry default pass. Two concurrent real processes publish exactly one complete app; injected competing empty destination is preserved. Failure retains only owned staging and returns its path. |
| AC-004 | passed locally/live | New manifest/dependency/toolchain/provenance validate; edited source is allowed. Invalid/conflicting provenance fails before runtime calls. Task-owned marker-only app validate/test/start passed without reintroducing release metadata; provenance restored after scoped stop. |
| AC-005 | passed locally/live | Offline installed snapshot list/create parity and old-snapshot independence from changed source default pass. Live source/installed list/show agree. Provider refresh was a ready no-op; existing app state/operations stayed stable. No provider rollback was performed against existing live apps; snapshot rollback compatibility was tested offline. |
| AC-006 | local/live passed; final acceptance pending | 110 focused tests, full repository checker and syntax/whitespace checks passed. Scoped live frozen install/test/build/typecheck, private page/health/assets and stop/source retention passed; second apps remain available. Runbook is written. CI/review, Daniel's final acceptance and merge remain pending. |

## Live generated-app workflow

`nextjs@1.0.0` release descriptor digest:
`de45b2d6e3d5fc3acdca4d275c41472336c04fde05c0f27103840b3abef22662`.
The selected release emits exact Node 24.21.0/pnpm 12.10.1 profile 1 using the
accepted SYS-002 registry. All original dependency/toolchain pins are retained.

Task-owned `/srv/forge/projects/prj003-acceptance` was created by:

```text
scripts/gptclawctl new prj003-acceptance --template nextjs --template-version 1.0.0
scripts/gptclawctl validate --project-root /srv/forge/projects/prj003-acceptance
scripts/gptclawctl deps install --project-root /srv/forge/projects/prj003-acceptance
scripts/gptclawctl test --project-root /srv/forge/projects/prj003-acceptance
scripts/gptclawctl start --project-root /srv/forge/projects/prj003-acceptance
```

| Operation | Observed outcome | CLI wall seconds |
|---|---|---:|
| Exact release creation | created; release provenance present | 0.478 |
| Frozen dependency install | complete; package/lock/workspace hashes unchanged | 10.453 |
| Test | tests-passed | 5.659 |
| Start, including build/typecheck/readiness | ready; private route configured; loopback 18084 | 31.396 |
| Ready no-op provider refresh | changed false; selected app not restarted | 1.644 |
| Installed-provider stop | stopped; source retained | 11.155 |

The actual private page/health returned 200 (7.116/0.112 seconds host-observed
response time). All 17 referenced Next.js assets returned 200. These are agent HTTP
checks, not a new desktop-browser confirmation. Installed provider reported 1.3.0
with `templates` capability; source and installed list/show output matched exactly.
All 19 generated source/metadata files matched their pre-stop SHA-256 values.

Hello World and Hello Second status before/after reported ready, no busy/error,
unchanged prior operation IDs and ports 18080/18081. Their private page/health pairs
returned 200 during acceptance and pages remained 200 after stop. No existing app
source, toolchain or service was changed. Shared ingress snapshot reconciliation
used the reviewed provider path; no per-app Serve/operator command ran.

## Legacy compatibility and final cleanup boundary

After the fixture was stopped, only its own release-provenance file was removed
for a marker-only legacy scenario. Installed validate/test/start passed; test took
2.183 seconds and warm start 4.655 seconds. None recreated the provenance file.
Installed stop passed in 10.780 seconds and the private page returned 404. The
original provenance bytes were restored after verifying no replacement existed.
The fixture is stopped; generated source, caches and owned receipts are retained
for review. No shared images/caches, unrelated fixtures or source were pruned.

## Local verification and development corrections

- `scripts/tests/test_private_apps.py`: 32 passed.
- `scripts/tests/test_project_dependencies.py`: 27 passed.
- `scripts/tests/test_project_toolchains.py`: 31 passed.
- `scripts/tests/test_project_templates.py`: 20 passed.
- Full `./scripts/check-repository.sh` passed in the prepared manifest environment;
  its initial run included 18 catalogue tests, before two added concurrency/default
  tests passed separately. Final full run outcome is recorded below.
- `scripts/check-template-releases.py`, Bash syntax, AST parsing of all eight changed
  Python files and Git whitespace checks passed.

Initial inventory creation encountered a pre-existing ignored package cache;
validation refused that asset. The cache was preserved at its original path,
excluded from inventory/staging and covered by a root node_modules ignore rule.
A `.` output-path fixture initially reached staging; validation now rejects empty
normalized path components before creation. Existing observation-only tests were
updated to compare pre-existing creation-lock contents/mtimes, rather than assume
creation produced no runtime directory. Their no-execution/no-write guarantees
remain tested. No failed run is counted as passing.

Local Terraform commands were not run because Terraform source did not change.
No infrastructure deployment, reboot, replacement, restore drill, additional stack
or automatic template upgrade is claimed. Remote CI and final source revisions
will be recorded below when available. PRJ-003 remains In review, not Delivered.

## Final local verification

The final full repository checker passed with all 110 focused tests, including
20 catalogue tests. Relative-link review resolved 169 local targets across eight
changed documentation files. Git staged/unstaged whitespace checks passed; no
cache, authentication or environment material is included in the staged changes.
