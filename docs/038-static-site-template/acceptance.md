# SPEC-038 — Static site acceptance evidence

Status: Verification in progress; not Delivered. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md) ·
[Runbook](../../runbooks/manage-static-sites.md) ·
[Implementation PR #92](https://github.com/danielbardsley/gptclaw/pull/92)

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | pending | Static generation/snapshot tests pass; release immutability passes against merged main `ba06d66`. Complete the stable full repository and CI runs. |
| AC-002 | pending | Frozen restore, format/lint/typecheck, three generated behavior/negative tests, real export and no-JS browser content pass. Complete generated unsupported-feature and compiled-image checks. |
| AC-003 | pending | Exported browser navigation/refresh/404 and HTTP escape/MIME/HEAD tests pass. Two actual private previews are under lifecycle verification. |
| AC-004 | pending | Six offline adapter tests cover generation, strict contracts, cache invalidation, failure state and snapshot packaging. Complete real edit/rebuild, failure recovery and independent-service/stop-retention scenarios. |
| AC-005 | pending | Automated axe WCAG A/AA, internal references and asset-budget checks pass. Deliberate generated defects are running; project-owner keyboard/focus/200%-zoom review remains pending. |
| AC-006 | pending | Generated quality/advisory and exported browser checks pass. Final generated image, broad checks, CI, timings/resource observations and owner acceptance remain pending. |

## Verification so far

Implementation checkpoint `a9a9192`, merged with reviewed main `ba06d66` in
`6ba0143`; final test/documentation follow-ups will be recorded separately.
Synthetic data only, as forge in rootless containers. No AWS, HCP, production,
public exposure, credentials, host package or shared ingress configuration change.

Executed locally:

- `python scripts/tests/test_project_static.py`: 6 passed.
- `python scripts/tests/test_project_manifest.py`: 28 passed after updating the
  formerly unsupported v10 case to v11.
- `python scripts/check-template-releases.py --baseline ba06d66`: passed; main
  advanced during this task, so its reviewed Python 1.0.1 releases were merged
  before establishing the new baseline. Historical releases were preserved.
- In the existing exact Node 24.21.0 / pnpm 12.10.1 container with 1 CPU,
  1536 MiB and 256 PIDs: frozen restore, check-only format, lint, strict typecheck,
  three behavior/negative tests, static build, links/budgets and security passed.
  Advisory result: no known vulnerabilities found.
- In the pinned Playwright image: exported navigation/refresh, axe WCAG A/AA,
  no-JavaScript content, skip-link keyboard behavior, actual 404 and narrow 200%
  text-size reflow checks passed. This is automated evidence, not owner acceptance.
- Export: 997,951 raw bytes total; per-page first-load JavaScript 176,338 gzip
  bytes, CSS 697 gzip bytes, HTML at most 7,554 raw bytes, local media 212 bytes.
  No external runtime references were found. All proposed budgets pass.
- `git diff --check`, staged whitespace check and shell syntax check passed.

The first staged build failed because Turbopack refused the dependency symlink;
webpack mode resolved it. Another build correctly refused source changes made
while it was running; the stable-source rerun passed. Browser network checks were
adjusted to ignore expected `net::ERR_ABORTED` navigation/prefetch cancellation
while rejecting other failures and unexpected HTTP errors.

An initial broad repository run overlapped release authoring and reported hash
mismatches. A fixture also needed new output-directory exclusions. These are not
passing broad-check evidence; a stable rerun is required. Terraform checks are
not applicable because no infrastructure source changed.

## Private fixtures and remaining work

The exact local-only source projects are `static-accept-one` and
`static-accept-two` under `/srv/forge/projects/`. Their loopback allocations are
18111 and 18112. Existing private ingress reports configured URLs; actual HTTPS
and lifecycle checks are still being recorded. One start returned busy after
its runtime activation during shared ingress reconciliation; observe its exact
state rather than resubmitting blindly.

The first creation attempt omitted `--local-only` and was refused by the existing
workflow credential policy before repository creation. The corrected local-only
commands created both fixtures; no policy/credential scope was broadened.

Retain both synthetic sources and owned runtime receipts. Do not remove unrelated
projects, snapshots or shared storage. Final implementation merge, final-head CI
and manual project-owner acceptance remain pending. The intentional guide pages
and leaf icon demonstrate the starter; downstream product adaptation must replace
or explicitly justify them against its own spec, with dependent links/tests updated.
