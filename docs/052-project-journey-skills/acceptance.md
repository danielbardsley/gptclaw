# SPEC-052 acceptance evidence

Owner: project owner. Observation date: November 1, 2026 (America/New_York).
Status: Source implementation; offline verification in progress. Merge,
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
  explicit Android selection, no-write retry and immutable-source inventory.
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
- `bash -n scripts/check-repository.sh` and tracked/staged whitespace checks pass.
  Final relative-link, mobile inventory and broad checker results are recorded
  below when complete. No Terraform files changed; Terraform tests are inapplicable.

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
| PJS-AC05 | Pending behavioral evaluation | Portable runtime and handover packages pass closure tests; readiness/unknown-outcome/stale-artifact cases await actual evaluator/consumer responses. |
| PJS-AC06 | Pending behavioral evaluation | Steering is generated and planning outlines reinforce it. Paired cases distinguish speculative hardening from an observed privacy blocker; table review is not a passed agent trial. |
| PJS-AC07 | Pending final checks/CI | Source integrity, failure/preservation, provenance, packaging and formatting checks pass; broad/final results and CI remain distinct below. |

## Limits and follow-up

The existing Android runner is a separate managed host. This workspace has no
available `adb` or emulator executable; no suitable scoped device fixture was
operated. Dogstats and other existing projects are excluded from adoption/testing
under this initiative. No host provisioning, cloud source upload, signing change,
public exposure, production action or data reset occurred.

[Behavioral cases](../../scripts/tests/fixtures/project-journey-skills/scenarios.md)
are ready for fresh-client/device evaluation with a reviewed synthetic fixture.
They specify expected dispositions and do not claim executed model/device behavior.
The project owner owns the supported-client/fixture follow-up and any separately
authorized installed-provider rollout. Retain pending acceptance until observed.
Revert source through a reviewed targeted change; preserve already-created
projects and their adaptations. Materialization failure preserves its marker and
published files for explicit recovery rather than resetting or overwriting them.
