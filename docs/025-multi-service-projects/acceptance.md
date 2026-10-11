# SPEC-025 implementation acceptance

- **Status:** Implementation and local/CI/live/client checks complete; review/merge pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-025](spec.md) · **Design:** [TDD-025](technical-design.md) · **Tasks:** [TASKS-025](tasks.md)
- **Implementation review:** [PR #58](https://github.com/danielbardsley/gptclaw/pull/58)
- **Provider/release:** `gptclawctl 1.7.0`, `notes@1.0.0`; project/catalogue v3, group receipt v2

The project owner authorized implementation and scoped synthetic verification on
October 11 with “Great, implement the spec.” The private notes fixture runs as
separate Next.js and FastAPI containers under one managed project. No infrastructure
apply, host package installation, public exposure, database, runtime secret injection
or live GitHub application repository creation occurred. Private runtime identity,
ports, node URL and ownership tokens remain in chat/local receipts, not this record.

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed | Offline v3 validation/generation tests cover unsupported versions/stacks, duplicate mapping keys, topology, escaping/overlapping roots and symlinks without executing app code. Existing web v1/API v2 suites pass. |
| AC-002 | passed | Exact grouped release/provenance/occupied destination checks and frozen per-component preparation pass. Actual stopped-group uv and pnpm add/remove transactions passed; existing transactional update/conflict/recovery suites remain integrated under the group lock. Registry/executable selection stays exact and existing defaults/releases are immutable. |
| AC-003 | passed | Group tests cover API-first ordering, partial second startup, reverse cleanup, unknown ownership, interrupted/active reconciliation refusal and busy locks. Actual managed start/status/test/logs/restart/stop passed; both components stop and source hashes remain unchanged. |
| AC-004 | passed | Actual private HTTPS UI, API, bundled docs/assets/schema, query and relative redirects pass. API and frontend syntax failures produce degraded readiness/unavailable routing and recover. Scope/port/resource inspection confirms separate containers, loopback publications and existing ceilings. Gateway protocol tests cover group APIs and blocked component routes. |
| AC-005 | passed | Real API and browser tests cover CRUD, bounded summaries/detail reads, pagination, missing/invalid/capacity input, plain text and failed drafts. Refresh/web reload retain notes; API reload/group restart clear them. Labels/keyboard/mobile checks pass. The project owner independently confirmed CRUD and the source-update text from the requested private desktop check. |
| AC-006 | passed | Exact-container quality and golden browser/contract/seeded-defect gates pass; critical coverage is 275/277 statements and 18/18 branches. All three configured workflows passed at final source `ca0080b`, including the multi-service Docker/browser/golden job. |
| AC-007 | passed | Independent synthetic standalone web/API fixtures remained ready through group failure/recovery/restart/stop. Scoped logs, distinct identities/ports and limits were observed. The committed pre-group provider refused v3 before execution on a stopped fixture and preserved selected source/manifest/lock hashes; a capable warm start restored it. |
| AC-008 | pending | Sanitized local/generated/CI/live/client evidence is recorded. Project owner confirmed “CRUD and update work” to the explicit create/edit/refresh/delete and “Two services, one project.” check. Implementation review/merge and post-merge feature acceptance remain; catalogue is In review, not Delivered. |

## Local and generated checks

Executed in the prepared isolated manifest environment:

- `./scripts/check-repository.sh`: the final source gate passed 436 tests,
  including browser backpressure/coalescing and declared-port regressions.
- Focused `scripts/tests/test_private_apps.py`: 36 tests passed, including real
  HTTP group forwarding, component-route refusal, waiting for a worker slot and
  explicit 503 saturation behavior. Focused `scripts/tests/test_project_groups.py`
  passed 16 tests, including one-second readiness expiry/mutation invalidation,
  ownership/lifecycle and declared-port/address-origin coverage.
- `.venv-manifest/bin/python scripts/tests/check_group_template.py /tmp/run006-browser-golden-4 --engine podman --reuse-api-image <verified-image> --reuse-node-image <verified-image>`: exact release generation, both frozen dependency graphs, API full quality, web type/test/build, isolated OpenAPI/CRUD and real browser checks passed. Image values are the existing reviewed identities, redacted here; full isolated CI builds them separately.
- Golden real seeded format/lint, strict type, notes behavior, static-security,
  broken-construction and insufficient-critical-coverage defects were rejected;
  source was restored and the positive coverage test rerun. API has 26 pytest tests;
  critical statements 275/277 (99.28%), branches 18/18 (100%). Black/isort/Ruff/mypy/
  pytest/coverage/Bandit/locked pip-audit and construction/OpenAPI build passed.
- Whitespace, changed Python compilation/Bash syntax and release integrity against
  `origin/main` passed. All 211 relative local links across changed planning/runbook/component README
  documents resolve; requirement/design/task/criterion coverage is consistent.

Local cold Node acquisition hit the existing nproc build limit. The isolated
checks reused already verified exact images/receipts with task-specific tags;
no host/resource limits were changed. CI proved clean builds separately. Public
advisory queries remained bounded; findings or unavailable data fail security.

Corrections are retained as evidence: test factories initially used runtime identity
rather than explicit test settings; browser fixtures needed their isolated dev
origin configured and detail-fetch/alert selectors synchronized with actual UI state;
Docker required explicit Containerfile selection. The live gateway initially revalidated
selected group API roots outside the trusted group context. Real browser asset bursts
also exceeded immediate worker admission, yielding 502. Group forwarding now uses
validated owned upstreams, the same 16 workers have bounded backpressure, and group
readiness/metadata work is coalesced for at most one second with tested invalidation.
No response/body/resource ceiling was broadened. Early release-hash checks during
concurrent authoring correctly failed; stable-asset reruns passed.

## CI

`d6b021b` passed all configured workflows, including the real multi-service Docker/
browser/golden job. Code revision `4081b12` passed:

- [Private application workflow #69](https://github.com/danielbardsley/gptclaw/actions/runs/38169062980): existing web/Python regression/golden and two-service Docker/browser/defect checks.
- [Development host #177](https://github.com/danielbardsley/gptclaw/actions/runs/38169062997): repository quality and configured Terraform validation/mock tests.
- [Tailscale federation #81](https://github.com/danielbardsley/gptclaw/actions/runs/38169062975): configured federation checks.

Final source `ca0080b`, including bounded browser admission/readiness and declared-port
regressions, passed all configured workflows:

- [Private application #71](https://github.com/danielbardsley/gptclaw/actions/runs/38171087514).
- [Development host #179](https://github.com/danielbardsley/gptclaw/actions/runs/38171087530).
- [Tailscale federation #83](https://github.com/danielbardsley/gptclaw/actions/runs/38171087512).

The subsequent documentation/evidence head is tracked on PR #58; source acceptance
is tied to `ca0080b`. Terraform
source did not change; no local Terraform checks or protected apply was executed.

## Managed EC2 and independent client behavior

Actual named managed operations used the source runner and installed immutable
provider through the existing private prefix. The two services each have 1 CPU,
1536 MiB and 256 PIDs, publishing only loopback, with an owned internal network.
The service ceilings sum to 2 CPU/3072 MiB/512 PIDs. Before the trial, the host
reported 7816 MiB total and 4918 MiB available; no resizing was requested/performed.

Measured initial project start was 59.204 seconds with cached verified profiles;
this is not a cold-host/image-download claim. Early warm start was 14.147 seconds;
subsequent managed warm start 17.191 seconds, real restart 32.786 seconds and stop
12.927 seconds. A visible web source update appeared in 0.809 seconds. Frontend
and API syntax errors became degraded; the API outage returned actual HTTP 503,
and both recovered after restoring only the selected source. Web reload preserved
an existing note; API reload and group restart reset the memory store.

Private HTTPS CRUD/invalid/missing/query/docs/assets/schema and relative redirect
checks passed. Stopped URL returned 404. Active dependency mutation and actual group
lock contention returned busy without source mutation. Group `test` passed both
components and a separate API/Node contract store. Eight-line component logs were
bounded; no payloads/environment or credentials were captured in evidence.

A digest-pinned Chromium job also exercised the real private HTTPS gateway without
API interception: CRUD, refresh retention, plain text, failed-draft preservation,
labels/keyboard and mobile layout passed. It is host-based browser evidence, distinct
from the independent project-owner desktop confirmation. The project owner answered
“CRUD and update work” to the explicitly requested create/edit/refresh/delete and
visible source-update-text check on October 11. This completes the client observation;
review/merge and final feature delivery remain separate.

## Remaining work and fixture disposition

Complete implementation review/merge and record the merged
revision/feature acceptance before marking the initial slice Delivered. Database,
cache, worker and arbitrary graph orchestration remain separate scope. Older providers
cannot operate v3 or interpret group receipts; stop/reconcile with the capable snapshot
before any rollback, preserving source and unknown resources. Ephemeral notes cannot
be restored.

The notes fixture is left running for the project owner with source retained. Earlier
standalone fixtures retain their prior disposition. Isolated check containers/networks
were removed by their owned bounded workflows; task-owned golden/cache directories and
images are retained for review. No shared image prune, broad cleanup, unknown-resource
removal, policy installer or unrelated runtime/data mutation was performed.
