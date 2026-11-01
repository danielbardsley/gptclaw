# TDD-052: Applicable skills and journey-priority guidance

Status: Implementation authorized November 1, 2026. Owner: project owner. Date: November 1, 2026.
[Specification](spec.md) · [Tasks](tasks.md).

## Approach and skill selection

Extend SPEC-050's creation-time guidance layer rather than editing immutable
application releases. Keep one explicit bounded resource/selection contract in
`scripts/project_guidance.py`, shared by bootstrap, catalogue creation and
provider packaging. Avoid scanning and copying arbitrary `.agents` contents.

| Capability | Package / reuse | Applicability |
|---|---|---|
| Planning | Existing `gptclaw-specification`, full assets | All projects |
| Current acceptance/handover | Existing `gptclaw-session-handover`, extend with acceptance reconciliation and its complete resources | All projects |
| Journey verification | New `gptclaw-journey-verification` | All projects; execute when a runnable interface exists; API/CLI journeys need no invented UI |
| Private environment operation | Existing `gptclaw-runtime-operation`, portable contract discovery plus references | Explicit runnable development capability; web, API and mobile/backend as applicable |
| Android operation | New `gptclaw-android-operation` | Explicit Android target, including mixed-stack projects |
| Native preview delivery | New `gptclaw-native-preview` | Android native build capability in this slice; iOS only after a separately reviewed adapter |

All means a local skill package is available, not that every task must invoke it.
A static web application receives runtime-operation when its selected starter
supplies a reviewed private lifecycle; a planning-only repository does not claim
one. Derive catalogue selection from validated manifest/template capabilities,
not name substring matching. Planning bootstrap accepts an explicit bounded
capability selection and records unknown stack honestly. Mixed stacks use the
union, copying shared packages once. Unsupported combinations fail clearly.

For a project that chooses its stack later, expose a documented preview/apply
materialization interface backed by the same fixed selection and immutable source
inventory. Choose exact CLI syntax during implementation after inspecting current
creation contracts. Record selected capabilities and source identity in project
provenance. Verify existing bundle-owned bytes before an idempotent no-op;
refuse adapted/unknown collisions with a proposed reviewed diff, never an overwrite.
Package the helper and required source resources so this later step can use the
project's recorded bundle without needing the original checkout. No fetching,
package installs, hook execution or broad adoption/repair mode is added.

## Portable operation contracts

Refactor runtime-operation's GptClaw-specific provider example into optional
provider documentation. Downstream skills must discover real local lifecycle,
compiler, native build, device and networking contracts from project guidance;
ship supporting checklists/assets and no hard-coded Dogstats paths or approval
exceptions. Preserve existing GptClaw runtime behavior. Missing commands generate
a concrete gap and leave independent diagnosis/planning available.

Android operation records exact serial/AVD, boot state, package and APK identity
before mutation. Use installed documented tooling, explicit target selection,
finite waits/log bounds and private evidence paths. Treat screenshots/UI dumps
as potentially sensitive. Test ordinary navigation and synthetic location through
real native controls; observe app-visible state and reopened persistence. Keep
upgrade data, distinguish app restart from device/emulator restart, and never
silently clear storage to make a scenario pass. Emulator installation and cloud
infrastructure remain out of scope.

Native preview builds use existing project scripts or a reviewed EAS contract.
Inspect archive contents before authorized upload; retain build ID for bounded
observation/reconciliation. Verify artifact identity/configuration and signing
compatibility before in-place installation. Do not embed secret values or sign
with production credentials. Build, install, journey and physical acceptance are
separate observations. No release-promotion skill is copied merely to obtain APK
preview support; retain it as a separate existing promotion workflow.

## Steering text and planning behavior

Propose a self-contained `docs/engineering/delivery.md` in the shared versioned
bundle, with a short required link from generated AGENTS.md (within 8 KiB).
Update planning/technical-design/task outlines and the specification skill to
require a principal journey, demonstration milestone and explicit deferred list.
Proposed central text:

> Prioritize a working application journey. Build the smallest approved slice
> that lets a user complete the principal task through the real application and
> reopen its persisted result. Demonstrate it early, then extend and harden it
> using observed failures and acceptance requirements. Choose each next task by
> how directly it enables or proves that journey. Defer speculative edge cases,
> broad refactors and optional polish with a reason and revisit trigger. Preserve
> required security, privacy, data-integrity and acceptance gates. If successive
> increments add hardening without advancing the journey, reassess the plan and
> move the next practical journey blocker first. Passing isolated tests does not
> establish a working journey or full product acceptance.

For a nonpersistent app, substitute its actual observable outcome for reopen.
Journey verification follows the approved visual reference when supplied and
records real rendered comparisons. Existing engineering rules still map to real
local/CI commands under SPEC-050; this initiative changes delivery ordering, not
formatter, typing, coverage or security thresholds. Adopt the text through the
creation layer and source templates, never the installed host policy. Do not
expand routine corrections into broad context audits.

## Components and verification

| Component | Planned responsibility |
|---|---|
| `.agents/skills/` | Reuse/extend three packages; create three missing workflows with bounded triggers and complete resources |
| `scripts/project_guidance.py`, `scripts/bootstrap-project.py` | Reviewed package inventory, capability selection, later materialization, validation and provenance |
| `scripts/project_templates.py` and provider packaging | Same selection/resources for application creation and installed-provider artifacts |
| `templates/projects/engineering/`, planning guidance and outlines | Versioned journey steering and required local links; preserve standards |
| Creation/operation runbooks and bootstrap skill | Exact supported selection commands, later stack selection, limitations and update procedure |
| Focused skill/creation tests | Behavioral scenarios, generated inventory, valid links, package closure, collisions and parity |

Extend the existing bootstrap/template/workflow/specification test suites and
add focused selection/materialization and behavioral fixtures. Use synthetic
projects and task-owned temporary directories. Include every supported catalogue
family, unknown-stack and mixed-stack selections, missing nested resources,
symlinks, adapted files, unchanged retry and output-size bounds. Verify that copied
packages and materializer can function with the original checkout unavailable.

Implementation checks: targeted Python suites, changed-shell syntax if any,
`git diff --check`, `git diff --cached --check`, the prepared offline
`./scripts/check-repository.sh`, and applicable template quality checks for
changed generation outputs. Record CI separately. No Terraform runs are needed
unless implementation introduces separately authorized Terraform changes.
Fresh-client discovery/use and a reviewed Android non-production fixture provide
behavioral acceptance beyond file/hash tests; absent tooling or authority leaves
those criteria pending. Tests must not create hosts or upload sources implicitly.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| PJS-001 | Inventory/reuse matrix and complete packages | PJS-T01–02 | PJS-AC01 |
| PJS-002, PJS-009 | Shared selection, both creators, later materialization, packaging/provenance | PJS-T03, PJS-T05 | PJS-AC02, PJS-AC07 |
| PJS-003–004 | Android/native preview contracts and observations | PJS-T02, PJS-T05–06 | PJS-AC03–04 |
| PJS-005, PJS-008 | Journey skill, steering and demonstration-first plans | PJS-T02, PJS-T04–06 | PJS-AC03, PJS-AC06 |
| PJS-006–007 | Portable runtime and concise acceptance/handover | PJS-T02, PJS-T05–06 | PJS-AC01, PJS-AC05 |

## Rollout and limitations

SPEC-050 merged in PR #107 (merge ea8d126). Implementation starts from main
07e66ab and retains its immutable release and shared creation-layer contracts.
The initiative was renumbered from draft 051 to 052 to preserve the Android
runner initiative already numbered 051 on main. Source delivery does not update an installed
provider. Any rollout follows the existing reviewed install path and authorization.
Use a targeted reviewed revert for regression recovery; retain generated projects
and their local adaptations. Reverting source cannot undo builds or runtime actions.

The project owner reviews the proposed names, capability matrix and explicit
later-materialization behavior with this design. No unresolved decision blocks
review of the draft; exact tooling is discovered rather than fabricated.

## Implemented interfaces

The shared inventory lives in `scripts/project_skills.py` and is consumed by
`project_guidance.py`; its standalone copy is `.agents/materialize-skills.py`.
Planning selection is repeatable `--capability runtime`, `--capability android`,
`--capability native-build` (requires Android). Explicit provider capability
mapping selects catalogue packages. Expo Go supplies runtime/Android operation;
development-build providers additionally supply native preview.

The optional resources are JSON text/hashes in
`docs/engineering/skills-bundle.json`; the current selection and helper/bundle
identities are `.agents/skills-selection.json`. `--check` writes nothing;
`--apply` adds only missing packages with exclusive writes. Existing active
adaptations or unknown package collisions stop with a reviewed-diff instruction.
A retained `.agents/skills-materialization-in-progress` marker prevents blind
retry after partial publication. Creation provenance is never rewritten by
materialization. Bundle version is 1.1.0, planning starter 1.2.0 and guidance
template 1.0.3. Both creators record source hashes and selected capabilities;
provider packaging carries the same full inventory.
