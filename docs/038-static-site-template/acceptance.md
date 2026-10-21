# SPEC-038 — Static site acceptance evidence

Status: Functional acceptance verified; final platform CI and merge pending.
Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md) ·
[Runbook](../../runbooks/manage-static-sites.md) ·
[Implementation PR #92](https://github.com/danielbardsley/gptclaw/pull/92)

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | passed | Seven offline static generation/contract/snapshot/inventory tests pass. Release immutability passes against `ba06d66`; default and historical releases are retained. The full repository checker passed in host-quality CI on `10e9676`. |
| AC-002 | passed | Frozen restore, check-only format/lint, strict types, three generated tests, real static export and no-JS browser content pass. The generated unsupported-cookie fixture fails build and cannot start stale output. The corrected compiled image serves pages/health/assets as uid 1000. |
| AC-003 | passed | Actual private HTTPS browser navigation/refresh/404 and HTTP escape/symlink/MIME/HEAD tests pass. Both sites' home, nested page, local SVG and health return 200. Unexpected HTTP errors and network failures fail browser checks. |
| AC-004 | passed | Both managed sites passed readiness. First-site managed test, edited-content rebuild, deliberate failed rebuild, exact-operation reconciliation, repair/rebuild, start, restart, stop/source retention and start passed. The second private site remained available throughout. An actual interrupted export in an independent fixture had no completion marker and startup refused it. |
| AC-005 | passed | Automated axe WCAG A/AA, reference crawler and budgets pass. Missing-alt, missing-route/image/fragment, formatting, lint/type and over-budget defects are rejected. The project owner explicitly confirmed manual navigation, keyboard focus and 200% zoom at desktop/narrow widths. |
| AC-006 | passed | Generated/compiled-image checks, budgets, runtime observations, verified instructions and owner UI acceptance pass. All eight application CI jobs, dashboard CI and complete host-quality CI passed on `10e9676`. The separately configured federation gate and implementation merge remain pending. |

## Revision and local verification

Initial implementation `a9a9192` was merged with reviewed main `ba06d66` in
`6ba0143`. Final packaging and inventory validation are at `c530b7c`; the remaining
follow-up adds the explicit broken-image CI case and this evidence. The new
unmerged release digest is
`e82772bc0c1d461edb6bb1a569bd3e893983cde9f73019a36574ba32c6d00060`.

Synthetic data only, as forge. No AWS, HCP, production, public exposure, credentials,
host package or Tailscale Serve/Funnel configuration change occurred. Managed
start reconciled its owned private ingress provider snapshot through the existing
reviewed interface. The installed snapshot resolves the final exact release.
The original `codex/dashboard-dark-mode` checkout remains clean and unchanged.

Executed locally with the existing isolated Python environment:

- `python scripts/tests/test_project_static.py`: 7 passed, including strict
  generation, source-cache invalidation, failed rebuild receipt, snapshot parity,
  supported web inventory and private app-route projection.
- `python scripts/tests/test_project_manifest.py`: 28 passed after moving the
  formerly unsupported v10 fixture to v11.
- `python scripts/check-template-releases.py --baseline ba06d66`: passed.
  Main's reviewed Python 1.0.1 patch releases were merged before this baseline.
- Existing pinned Node 24.21.0 / pnpm 12.10.1 container: frozen restore,
  format/lint/typecheck, three behavior/negative tests, static build,
  references/budgets and security passed. Advisory result: no known vulnerabilities.
- `python scripts/tests/check_static_template.py <owned-fixture> --engine podman
  --image localhost/gptclaw-node:24.21.0-pnpm12.10.1`: generation, frozen restore,
  generated gates, formatting/lint/type/reference defects, missing-alt browser
  refusal, unsupported cookies/build refusal and repaired export/browser passed.
  Its initial compiled-image step failed due to the missing profile; that specific
  step was corrected and rerun successfully, followed by an unprivileged image
  smoke test. This is not presented as an uninterrupted passing script run.
- Pinned Playwright image, both locally served export and the actual private
  second site: navigation/refresh, axe WCAG A/AA, no-JavaScript content, skip-link
  keyboard behavior, true 404 and narrow 200% text-size reflow passed. Manual
  owner confirmation independently covers the requested UI/zoom acceptance.
- Independent task-owned fixture: `timeout --signal=TERM --kill-after=2 2 node
  scripts/build.mjs` interrupted export; no completion marker remained and
  `node scripts/serve.mjs` refused startup. No managed worker was killed.
- Corrected compiled image `4b06be37f148`: uid 1000; home, nested page,
  readiness and SVG HTTP checks passed on an ephemeral loopback port. Its owned
  smoke container was then stopped; no shared image/storage pruning occurred.
- Broken exported image reference was injected in the disposable generated
  fixture, rejected by the crawler, and the original file restored.
- `git diff --check`, staged whitespace and `bash -n scripts/check-repository.sh`
  passed. All 272 relative documentation links passed; the final review worktree and
  original checkout were clean at delivery.

The clean local `./scripts/check-repository.sh` run passed lifecycle (36),
dependency (27), toolchain (31), catalogue (23), and other completed suites, but
reported one existing Metro timing-test failure:
`ProxyTests.test_expiry_closes_stalled_transfer` in `test_metro_proxy.py`. That
fixture arms a 150 ms lease before its HTTP exchange; the host also logged event
loop delays exceeding 150 ms. The isolated case passed unchanged (0.207 s), and
the entire unchanged 29-test Metro proxy suite then passed (6.104 s). This is
consistent with a scheduling-sensitive fixture, not evidence of a static-adapter
regression; no Metro source or test was changed.

The full repository checker independently passed on the identical committed
revision in host-quality CI. The remaining duplicate local run was then explicitly
interrupted to release its task-owned fixture resources. It is not claimed as a
passing local full-script execution. The earlier authoring-time run, which
reported release-hash mismatches during edits, was also stopped rather than
claimed successful. Copied-repository fixtures exclude static output/staging.

Local Terraform runs were unnecessary because infrastructure source is unchanged.
Host-quality CI nevertheless passed Terraform formatting, validation and tests;
its protected remote plan/apply jobs were skipped. No infrastructure was deployed.

## Private runtime evidence

Both retained exact-source fixtures are ready:

- [static-accept-one](https://forge-dev-01-4.tail8c3304.ts.net/projects/static-accept-one/),
  source `/srv/forge/projects/static-accept-one`, loopback port 18111.
- [static-accept-two](https://forge-dev-01-4.tail8c3304.ts.net/projects/static-accept-two/),
  source `/srv/forge/projects/static-accept-two`, loopback port 18112.

First-site operation evidence (seconds include validation and dependency/build
work, not only HTTP readiness):

| Action | Operation / result | Seconds |
|---|---|---:|
| Cold start | `a0f9d2801bad478381cf1723fc15734a`, ready | 237.953 |
| Managed test | `963f9665f9864d84a00faefe5214eced`, passed | 21.183 |
| Edited source rebuild | `dcf67cbadab6487b889e1259aae07618`, succeeded; changed text observed over HTTPS | 197.228 |
| Deliberately invalid source rebuild | `1dfa2f593262458cb1a4ca4f787b4d85`, failed and exact guard reconciled; route unavailable, second site healthy | 102.192 |
| Repaired rebuild while stopped | `5dffe2f18baa4ebc851218053841524f`, succeeded and remained stopped | 120.657 |
| Start after repair | `2990fbdf8b464b4785b5b15d10230569`, ready | 145.634 |
| Restart | `dd1959dd6f934936ad75d65e8bc0f703`, real stop/start transitions, ready | 177.608 |
| Stop | `05dbb7f1fca545f99e643db08e6a7e03`, route removed and source bytes retained | 20.149 |
| Start after stop | `4a1862f3edca4a64ad0168595ac4d449`, ready on retained port | 128.214 |

The second site's start returned busy after runtime activation during shared
router reconciliation; status confirmed the same operation
`6fb81e2f562246138e663ef71c2a0522` ready with no active job. Both private HTTPS
routes passed, without blindly submitting a duplicate start. A later ready
start reconciled the final provider snapshot and returned `changed: false`.

Actual private second export: 998,755 raw bytes total. Maximum per-page assets:
176,357 gzip JS bytes; 697 gzip CSS bytes; 7,650 raw HTML bytes; 212 local-media
bytes. No external runtime references. All budgets pass. An idle observation was
39.79 MB memory, 0.16% CPU and 24 PIDs; inspected limits were 1,610,612,736 bytes,
256 PIDs and 100000/100000 CPU quota/period (one CPU). Health reached readiness
within the existing post-service-start deadline. Overall cold-start/build timings
above include frozen acquisition/export and are not claimed to fit that health-only
deadline.

The two synthetic fixtures were generated from the draft release. After correcting
build packaging, exactly `Containerfile` and the new `checks/node-profile.json`
were refreshed to the final unmerged inventory; all starter bytes were verified.
Earlier draft receipts are retained as `.gptclaw/template-release.draft.json`;
current receipts identify the final digest. Runtime source/output and the
manually accepted UI did not change during that packaging refresh.

## Failures, retention and remaining delivery

Turbopack initially refused the staged dependency symlink; pinned webpack mode
resolved it. A separate build correctly rejected a concurrent source edit; the
stable-source rerun passed. Browser checks exclude expected `net::ERR_ABORTED`
navigation/prefetch cancellation and still reject other failures/unexpected HTTP
errors. The compiled-image profile omission was fixed with the exact reviewed
profile and registry-equality validation; standalone image verification then passed.

The first fixture creation omitted `--local-only` and was refused by workflow
credential policy before repository creation. Corrected local-only commands
created both fixtures; no permission scope was broadened.

Retain both fixture sources/receipts and private previews for review. Owned ephemeral
smoke containers were stopped. No unrelated project or published release was
modified. The guide pages and leaf icon intentionally demonstrate this template;
product adaptation must replace or justify them and update dependent links/tests.

## CI and review handover

Verified implementation revision: `10e96760ee0719e1729b28cc66f8c07fd761d21b`.
The following checks ran on that exact revision:

- [Application workflow](https://github.com/danielbardsley/gptclaw/actions/runs/39548878091):
  passed, all eight jobs including static-site, default template, APIs, mobile,
  groups and database checks.
- [Dashboard workflow](https://github.com/danielbardsley/gptclaw/actions/runs/39548877940): passed.
- [Host-quality workflow](https://github.com/danielbardsley/gptclaw/actions/runs/39548878036):
  passed, including the entire repository checker and Terraform format/validate/test.
- [Federation workflow](https://github.com/danielbardsley/gptclaw/actions/runs/39548877935):
  still in progress at this evidence update; do not infer its result from other runs.

This final evidence update changes documentation only. Its subsequent CI is
separate from the verified implementation revision above. Remaining: the
federation/final evidence CI gates, PR review and merge. Manual UI acceptance is
complete; it does not imply merge or a broader owner disposition. Mark TPL-005
Delivered only after merged implementation and the repository's remaining gates.
