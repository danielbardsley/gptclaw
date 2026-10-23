# SPEC-049 acceptance tracking

- **Status:** Implementation in review; security/cloud/device acceptance open.
- **Owner:** Project owner
- **Evidence date:** 2026-10-23 (America/New_York)
- **Scope:** Android-first development clients, supporting MOB-005/006 slices.
- **Source:** `codex/mob-004-development-builds`, based on planning commit
  `f29c6fc` and main `6375986`; implementation revision recorded after commit.
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
