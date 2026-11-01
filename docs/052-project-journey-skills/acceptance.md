# SPEC-052 acceptance evidence

Owner: project owner. Observation date: November 1, 2026 (America/New_York).
Status: Source implementation complete at `16e615c`; offline and independent
synthetic verification passed. Full acceptance remains pending. Merge,
installed-provider rollout, fresh-client behavior and live Android qualification
remain separate. [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md).

## Source and scope

Implementation is based on main `07e66ab`; SPEC-050 merged through PR #107
(`ea8d126`). The project owner approved the draft and requested implementation in
this chat on November 1. Draft SPEC-051/PR #115 is superseded by SPEC-052 because
main had already allocated 051 to the Android runner. PJS IDs are preserved.

Three new skill packages cover Android operation, native preview and journey
verification. Specification, runtime-operation and session-handover are reused
and extended. Planning starter 1.2.0 and engineering/skills bundle 1.1.0 supply
common skills plus explicitly selected operational packages. Application creation
uses the reviewed provider capability mapping. Template 1.0.3 and generated root
guidance prioritize an early demonstrated principal journey with essential gates
preserved. No installed policy/provider or existing application was changed.

## Executed offline and generated-output checks

- `scripts/tests/test_project_skills.py`: **17 passed**. Exact selection and
  mixed-stack union, offline isolated-Python invocation, preview/no-op, later
  Android/native selection, adaptations/collisions, unrelated skills, missing
  resources, source/bundle/helper integrity, link failures, symlinks and retained
  partial-operation markers are exercised with synthetic task-owned fixtures.
- `scripts/tests/test_project_bootstrap.py`: **32 passed** after correcting the
  new test to expect the helper's documented wrapped `BootstrapError`. Includes
  explicit Android selection, no-write retry and immutable-source inventory. Final committed-source rerun: **32 passed** in
  **15.314s**.
- Final focused template tests: **3 passed** in **66.991s**: all **11** provider
  families receive exactly selected skills and hashes, collision preserves bytes,
  and a packaged provider creates matching output without the original checkout.
  An earlier full **28-test** template run had one outdated collision-exception
  assertion; the source now retains `FileExistsError` and that case passes.
- Workflow skills: **9 passed**; specification skill: **10 passed**; repository
  guidance: **10 passed**. The skill-creator validator passed for all three new
  packages. Packaging tests are not proof of agent behavior.
- Prettier **3.9.10** checked actual generated roots of Expo React Native 1.1.0,
  Expo Notes 1.1.0, Expo Development 1.0.0 and Expo Development Notes 1.0.0:
  **all passed**, with their real config/ignore rules and a network-disabled
  rootless Node container. No formatting exclusions were added. Short capability
  arrays are emitted in the existing formatter's canonical layout. The formatter
  alone was installed into a task-owned temporary directory; no host packages.
- Final mobile exact-inventory/identity regression: **1 passed** in **13.404s**.
- The committed candidate CLI passed preview, create, unchanged creation retry,
  isolated offline materialization preview/apply and unchanged retry; its task-owned
  fixture was removed. Release completeness/immutability versus main passed.
- **420** real relative file links in changed Markdown (outside code examples)
  passed review. Legacy Expo 1.0.1 also passed Prettier after repository-guidance
  adaptation.
- An [independent synthetic behavioral pass](behavioral-evaluation.md) passed all
  **six** supplied requests without intended-answer guidance: paired delivery/
  privacy priorities, runtime reconciliation, stale-artifact handover, ambiguous
  Android target and preview mismatch. No live operations were performed.
- `bash -n scripts/check-repository.sh` and tracked/staged whitespace checks pass.
  Final relative-link, mobile inventory and broad checker results are recorded
  below. No Terraform files changed; Terraform tests are inapplicable.

The principal delivery journey has actual executable evidence: generate a
self-contained planning project, preview additions without writes, materialize
Android packages through the copied helper in isolated Python, then retry without
writes. It neither installs Android tools nor claims a working native application.

## Acceptance matrix

| Criterion | State | Evidence / remaining work |
|---|---|---|
| PJS-AC01 | Passed offline | Reviewed six-capability inventory, complete local packages, portable runtime references and isolated helper execution. |
| PJS-AC02 | Passed offline | Planning creation/selection regressions, all 11 catalogue providers, mixed-stack selection, adaptation preservation and no-write retry. |
| PJS-AC03 | Pending live/client evidence | Device procedures and review cases are shipped; no fresh-client discovery or actual emulator upgrade/journey was executed in this task. |
| PJS-AC04 | Pending live observation | Private preview identity/upload/reconciliation procedures and review cases exist; no scoped non-production build/install was executed. |
| PJS-AC05 | Passed synthetic evaluation | Independent runtime response retained operation identity/readiness uncertainty; handover consumer received the actual installed blocker and next build/upgrade/journey action. |
| PJS-AC06 | Passed synthetic evaluation | Generated steering and outlines plus independent paired responses defer optional hardening, prioritize the broken real journey, retain privacy gates and refuse mock-only completion claims. |
| PJS-AC07 | Partial; release CI failures | Integrity/preservation, provenance, packaging, formatting and full repository CI pass; generated-release dependency gates and the opaque legacy job remain unpassed. |

## Limits and follow-up

The existing Android runner is a separate managed host. This workspace has no
available `adb` or emulator executable; no suitable scoped device fixture was
operated. Dogstats and other existing projects are excluded from adoption/testing
under this initiative. No host provisioning, cloud source upload, signing change,
public exposure, production action or data reset occurred.

[Behavioral cases](../../scripts/tests/fixtures/project-journey-skills/scenarios.md)
include review criteria; six raw requests now have independent agent-response
evidence. Fresh-client discovery and real device cases still need a reviewed
synthetic fixture and are not established by those responses.
The project owner owns the supported-client/fixture follow-up and any separately
authorized installed-provider rollout. Retain pending acceptance until observed.
Revert source through a reviewed targeted change; preserve already-created
projects and their adaptations. Materialization failure preserves its marker and
published files for explicit recovery rather than resetting or overwriting them.

## CI observation at source `16e615c`

[Quality matrix](https://github.com/danielbardsley/gptclaw/actions/runs/41339369123):
metadata and the full Fastify cell passed. All ten failed generated-release
cells were inspected and fail dependency-security checks against unchanged
release locks/advisory policies. The [development-host quality job](https://github.com/danielbardsley/gptclaw/actions/runs/41339369122)
passed the complete repository checker (**1,024 Python tests in 54 suites**,
plus its shell/invariant checks), Terraform formatting, initialization, validation
and Terraform tests. Its deployment jobs were skipped. The separate Tailscale
quality job was still running when last observed; no deployment was requested.
[Private workflow](https://github.com/danielbardsley/gptclaw/actions/runs/41339369156)
Python, multi-service and development-database job logs show dependency-security
failures against
unchanged release locks (`filelock` 4.1.1 and `virtualenv` 21.14.6 advisories).
The legacy mobile-source job reports an opaque generated-workflow failure whose
child log is only referenced in the remote temporary directory; its root cause
is not established. The matching legacy generated output passed local formatting. Static-site and
mobile/backend jobs also fail their dependency-security gates; TypeScript API
passed.
No audit suppression, release mutation, waiver renewal or dependency upgrade was
introduced. Aggregate CI is not green and is not claimed as passing.

## Final local check disposition and handover

The broad local diagnostic command was
`PATH="$PWD/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh`. It completed
**772 Python tests across 34 suites**, with one early outdated bootstrap-test
expectation (the wrapper raises `BootstrapError`, not bare `ValueError`). That
expectation was corrected; the final committed bootstrap suite passed all 32.
After the complete checker passed in CI at `16e615c`, the superseded local run
was intentionally interrupted during the next suite (exit 143). It is not claimed
as a green complete local run. No additional recorded suite failed.

Final source remained unchanged after `16e615c`; the evidence-only follow-up adds
these results and the synthetic evaluation requests/report. The task-owned
formatter and generated/evaluation fixtures were removed. The unrelated original
untracked `oom` file remains untouched. PR #116 targets main; merge and provider
rollout are pending. The new source CLI is tested, while the installed provider
and existing projects retain their previous bytes.
