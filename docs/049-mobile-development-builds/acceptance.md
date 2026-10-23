# SPEC-049 acceptance tracking

- **Status:** Implementation in review; security/cloud/device acceptance open.
- **Owner:** Project owner
- **Evidence date:** 2026-10-23 (America/New_York)
- **Scope:** Android-first development clients, supporting MOB-005/006 slices.
- **Source:** `codex/mob-004-development-builds`, based on planning commit
  `f29c6fc` and main `6375986`; implementation commit `e79e09a`. Corrective
  regression updates follow on the same PR; final source revision `b871a6b`.
- **Review:** [PR #99](https://github.com/danielbardsley/gptclaw/pull/99)
- **Plans:** [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Pending | Offline schema 11/12 generation, static native identity, explicit configuration/binding and legacy profile refusal are implemented/tested. Real account/project binding and installed capable-provider behavior remain unobserved. |
| AC-002 | Pending | Owner selected previous-account reuse, Expo-managed signing, willingness to pay and 30-day retention in this chat. Exact account/project, credential privilege/custody readback, certificate fingerprint, budget and actual artifact settings remain pending. No credential or billing changes occurred. |
| AC-003 | Failed | Exact source/tool locks and deterministic inspected archive tests are prepared. Standalone/bound format/lint/types/component tests and unsigned Android exports pass. Full source verify fails on the unapproved transitive Zod advisory; real cloud compiler compatibility is unobserved. |
| AC-004 | Pending | Synthetic tests cover durable intent, lost responses, duplicate refusal, budget bounds, remote identity, reconciliation and explicit no-job attestation. Authorized real job submission/recovery remains unperformed and audit-blocked. |
| AC-005 | Pending | Real pinned apksig container accepts a signed synthetic APK and rejects its unsigned counterpart; metadata parser and safe artifact URLs are checked. No EAS APK was retrieved or installed and no physical private native launch was observed. |
| AC-006 | Pending | New MMKV probe component passes synthetic interaction/failure tests; native fingerprint/launch tests distinguish JS edits and required rebuilds. Actual module behavior and replacement binary installation on Android remain pending. |
| AC-007 | Pending | Bound starter retains existing typed FastAPI notes contracts; source tests cover binding/independent lifecycle boundaries. No new live backend/database/device operation or native outage/persistence acceptance was performed. |
| AC-008 | Pending | Whitespace, targeted Python/shell checks, worker boundary tests and source checks are recorded below. Final broad local/CI results, merge, installed parity, capable rollback/owned cleanup and owner acceptance remain separate gates. |

## Executed local verification

All checks used synthetic fixtures, the existing Python 3.12 manifest environment
and rootless containers. No host packages, Expo credentials, production data or
public routes were used.

- Initial `python -B scripts/tests/test_native_builds.py`: 19 tests passed before
  additional recovery/artifact/provenance checks. Later development runs caught a
  queued-launch refusal and an incorrect test access to the repository-plan wrapper;
  both were corrected. The final registered suite result is recorded separately.
- `python -B scripts/tests/test_project_manifest.py`: 28 tests passed after moving
  the deliberately unsupported-version fixture from 11 to 13. Schemas 11/12 are
  now intentionally supported; historical schemas are unchanged.
- `python -B scripts/tests/test_metro_state.py`: 16 tests passed, including a
  separate HTTPS-only development-client receipt and Android-only projection.
- `python -B scripts/tests/test_apk_metadata.py`: 3 tests passed for bounded binary
  manifest parsing and malformed/missing package rejection.
- Pinned Node container `node --test scripts/tests/eas_worker.test.cjs` with the
  worker/test mounted at their declared `/provider` and `/test.cjs` paths and
  network disabled: 3 tests passed. Exact archive bytes, tamper refusal and
  inherited-variable refusal are covered without credentials or requests.
- Official pinned JDK/apksig image built successfully after fixing downloaded
  library readability for the unprivileged verifier. A task-owned synthetic key
  signed a synthetic APK using apksig. Verification passed for the signed file;
  the unsigned counterpart returned exit 1. This is software verification, not
  an application build or real signing-key acceptance.
- Both starters ran `pnpm install --lockfile-only --ignore-scripts` under the
  reviewed Node 24.21.0/pnpm 12.10.1 image to freeze inputs. Their lockfiles match.
  Standalone dependencies were installed frozen/without scripts; bound source
  checks mounted that exact matching dependency graph read-only.
- Both ran `pnpm exec prettier --write .` and `node checks/quality.cjs verify`.
  Format, lint and strict types passed. Standalone Jest: 3/3 tests, 100% covered
  component statements/branches/functions/lines. Bound Jest: 12/12 tests across
  three suites, 93.63% statements / 82.38% branches / 91.48% functions / 97.26%
  lines. Both also passed their three source-security behavior unit tests.
  Full verify stopped at the real dependency audit; it did not pass.
- Separate network-disabled `node checks/quality.cjs build` completed for both
  Android targets, producing approximately 2.7 MB bundles and metadata. These are
  unsigned JavaScript/assets, not development APKs or physical-device evidence.
- `npm audit --json` for frozen EAS CLI 25.3.0: 9 high, 0 critical vulnerable
  package entries. Source `pnpm audit --json`: 2 high, 0 critical. See the
  [security disposition](security-review.md) for exact findings and gates.
- Python compilation of changed modules, `bash -n scripts/check-repository.sh`,
  `git diff --check` and `git diff --cached --check` passed at the recorded stages.

Early broad checks loaded release metadata while it was still being edited and
reported catalogue-integrity failures, alongside the now-corrected version fixture.
Those in-progress runs were superseded; they are not passing final evidence.
A stable final `./scripts/check-repository.sh` run is in progress. No CI or
Terraform result, deployment, device behavior or acceptance is inferred from it.
Terraform checks are inapplicable to this source-only change.

## Starter adaptation and operational limits

Standalone source replaces the counter/about demo with the native storage probe.
The notes variant deliberately retains the notebook, typed notes API contracts,
synthetic CRUD and supporting health/docs behavior, adding the native probe.
Dependencies, imports, tests, native identity/configuration, architecture and
quality metadata are updated together. Existing published starters are unchanged.
Rendered physical UI and live exposed API behavior have not been observed here.

No EAS or signing secret entered source, upload staging or logs. Native source and
EAS security gates remain blocking; existing Go/source advisory exceptions were
not broadened to native signing/runtime. The owner still needs exact external
scope and artifact access/cost decisions. Retention eligibility is capped at
30 days; external retention/local deletion require recorded operator follow-through.
No remote artifact/key deletion or retention automation was created.

The isolated worktree preserves the original dashboard branch and unrelated
working trees. Local task containers did not change running applications,
listeners, database data or the installed provider. Implementation merge and
Android owner acceptance remain pending.

## Corrective regression follow-through

The stable broad run executed all 26 native build regressions successfully and
all three APK parser cases. Targeted launch/provenance/audit checks (3) and native
tool-image/foreign-job checks (2) also passed. Review added scoped job-ID retention
when queued remote metadata is incomplete; its focused test is tracked separately.

The broad run caught a legacy spike regression: bare source-only spike fixtures
have no manifest. Native configuration dispatch now handles that case without
weakening the original Go config restrictions. All 24 spike tests and 9 dashboard
Metro projection tests passed after correction. CI caught an expected capability
assertion still listing session schemas 1/2; the collector and Metro contract tests
now include schema 3. The corrected collector suite passed 7 tests.

`check-template-releases.py --baseline origin/main` passes after explicitly tracking
the release's disabled, public synthetic backend default (normally ignored in
generated projects). Catalogue 9 and native profile 2 now participate in historical
immutability checks. No pre-existing published release was changed.

CI on `e79e09a` began all five repository workflows; the dashboard job failed its
old session-schema assertion before browser tests. That is not a passing CI result.
Corrective CI, final broad outcomes, security resolution and native external/device
acceptance remain distinct.

## Final corrective evidence

- Full corrected template fixture suite: 24 tests passed. It now copies both
  native helper toolchains into installed-snapshot fixtures and expects catalogue
  version 9. Frozen historical releases remain unchanged.
- Full corrected Metro contract suite: 20 tests passed. Dashboard collector 7,
  dashboard Metro 9, legacy spike 24 and Metro state 16 tests passed.
- The complete native suite passed 31 tests before the final account-wide budget
  regression was added. The final expanded result is recorded below.
- The worker's three Node VM tests also passed with the CI resource limits,
  read-only container filesystem and network disabled.
- On corrective commit `b68d371`, dashboard CI passed. The Tailscale workflow's
  complete repository check finished with only the two template-fixture failures
  listed above, subsequently corrected and rerun locally. Its protected apply and
  plan jobs were skipped. This was a failed CI run, not a deployment.
- Private application and quality matrix CI failed. In addition to the corrected
  template fixtures, real audits rejected native/Expo source dependencies and
  existing immutable Next/Python starter dependency graphs. Fastify passed;
  matrix metadata (including the native worker tests) passed. These failures
  are not waived. The final corrective commit requires fresh CI.

The owner has not supplied billing details or approved a numeric budget. The
recommended starting point is Expo Free; $25 total for the first month is a
proposed ceiling if paid access is needed, not authorization to subscribe.
No cloud job, credential read, signing-key operation, provider rollout or physical
Android installation occurred. Task-only dependency/export files and synthetic
signing material were removed; public source/locks and sanitized evidence remain.


Final source verification at `b871a6b`: `python -B
scripts/tests/test_native_builds.py -v` passed all 32 tests in 292.768 seconds,
including shared-account approval enforcement across projects. Frozen catalogue
baseline integrity and local Markdown links passed; changed Python modules
compiled and shell/whitespace checks passed. Fresh CI started all five workflows
and remains pending at handover. The local broad checker remains running through
repository-credential fixtures; its earlier corrected failures mean that run
cannot be reported green. No final full-check success is claimed.

Source and evidence are committed/pushed on the isolated feature branch. The
original dashboard worktree has no uncommitted changes and was preserved. Remaining
work: resolve audit findings through reviewed compatible tooling, obtain exact
external configuration and numeric approval, complete CI/review/merge, then conduct
the separately gated remote build and Android acceptance. No Delivered status.
