# SPEC-052: Project skills and working application journeys

Status: Approved; implementation authorized November 1, 2026. Owner: project owner. Date: November 1, 2026.
Feature: AGT-011. [Design](technical-design.md) · [Tasks](tasks.md).
The project owner approved this specification and requested implementation on
November 1, 2026. Installed-provider rollout and existing-project adoption remain
outside this scope. This initiative was drafted as SPEC-051 in PR #115; it is
renumbered SPEC-052 because main already uses 051 for the Android runner. Stable
PJS requirement, task and acceptance IDs are unchanged.

## Outcome and scope

New projects receive complete, applicable local skills for planning, operating,
building and verifying a working application. Project guidance makes the first
working user journey the main delivery milestone, followed by evidence-driven
hardening. Agents should not spend successive increments refining hypothetical
edge cases while the application cannot perform its principal user task.

Cover both planning bootstrap and catalogue application creation, including
provider packaging and a later, separately authorized installed-provider rollout.
Build on [standards inheritance](../050-project-standards-inheritance/spec.md).
Reuse existing skills where suitable; create missing workflows rather than
copying duplicate skills with overlapping triggers. Include specification,
Android emulator operation, native build/preview delivery, product journey
verification, private development operation, and acceptance/handover support.

Exclude changes to Dogstats or other existing projects, emulator provisioning,
host repair, public exposure, infrastructure changes, production promotion,
store submission, new app frameworks and automatic skill synchronization.
Creating skill files neither installs the tools they describe nor authorizes
operations. No new agent personas are required.

## Evidence and reuse

At planning time the local repository contains the specification, runtime-operation,
session-handover and release-promotion skills. It has no dedicated Android
emulator, native preview or product-journey verification skill. The current
shared creation inventory copies only the specification skill and engineering
standards. Runtime-operation contains GptClaw-specific provider references and
must be made portable before downstream copying. Release-promotion governs
existing product promotion pipelines; it does not replace native preview delivery.

Dogstats' November 1 native walkthrough found retry/timer/Save issues despite
passing source checks. In-place APK upgrades preserved app data, and synthetic
emulator observations remained separate from phone GPS/battery qualification.
Its local core-flow and preview documents informed this proposal; no Dogstats
files, accounts, endpoints, exception approvals or private evidence are copied.

## Requirements

- PJS-001: Maintain a reviewed inventory mapping each requested capability to an
  existing skill or a new package, with applicability, all supporting resources,
  source/version identity and a clear trigger. Retain the specification skill;
  reuse and extend runtime-operation and session-handover. New skill names in
  the design are proposed names, finalized through implementation review.
- PJS-002: Both creation paths copy complete project-owned packages selected
  deterministically from explicit stack/capability metadata. Planning projects
  of unknown stack receive common planning, journey and handover guidance;
  operational skills are added through a documented explicit selection at
  creation when capabilities are known. Supply an idempotent, reviewed local
  materialization command for later stack selection, limited to missing
  bundle-owned files; preview changes, preserve adaptations and reject collisions.
  Mere future availability in GptClaw does not satisfy delivery. Existing
  projects require separately authorized adoption, never background updates.
- PJS-003: Android operation resolves the exact available device and reviewed
  command contract, verifies boot/readiness, upgrades without data loss, launches
  and exercises native UI, collects bounded sanitized evidence, and supports
  synthetic location, background/return, connectivity loss and restart scenarios.
  It preserves app data and unrelated devices; uninstall, storage clearing,
  emulator wipe and host provisioning are outside its default scope. Missing
  capability blocks only dependent actions. Emulator evidence must not be
  reported as physical GPS, battery, lock-screen or accessibility qualification.
- PJS-004: Native preview delivery selects the project's actual local/EAS build
  interface, inspects upload inputs and artifact privacy, binds source/build ID
  to APK hash/package/version/signing identity and intended public configuration,
  verifies upgrade compatibility and records installation separately. Preserve
  private artifacts and development/production signing separation. Honor already
  authorized cloud submission; never infer upload/store/promotion authority
  from a request to prepare a build. Reconcile outstanding builds before retry.
- PJS-005: Journey verification uses approved user outcomes and design references,
  starts with a thin runnable UI-to-service-to-storage slice, exercises the real
  interface and reopened persisted result, then relevant failure/retry/restart
  cases. Label doubles, synthetic inputs, screenshots and physical observations.
  Run focused regression checks for observed defects; compare actual rendered
  UI with the approved visual reference where one exists. Never replace actual
  native interaction with API-only or component-test claims.
- PJS-006: Private development operation discovers project-owned lifecycle and
  readiness contracts for the required backend/components/Metro and device
  connectivity. Preserve data and private access, use bounded diagnosis and
  operation reconciliation, and never improvise process killing, host repair or
  infrastructure mutation when an interface is absent. Copy portable references;
  no dependency on the original GptClaw checkout may remain.
- PJS-007: Reuse session-handover and specification acceptance support, adding
  concise current journey status, exact source/artifact/installed identity,
  actual local/CI/runtime/device findings, outstanding operations and the next
  useful action. Keep dated history, distinguish report freshness, and avoid
  duplicating acceptance ledgers. Support acceptance reconciliation when asked;
  do not generate a large handover after every small change.
- PJS-008: Deliver the journey-priority steering text in generated AGENTS.md or
  a local document required and linked by it, and reinforce it in planning/task
  outlines and journey verification. Plans name one principal journey, a bounded
  first demonstration milestone, necessary gates and deferred work. At each
  checkpoint choose the next action that most directly enables or proves that
  journey. Defer speculative edge cases, broad refactors and optional polish;
  record rationale and a revisit trigger. Interrupt for observed journey blockers,
  security/privacy/data-loss risks or required acceptance gates. Repeated
  hardening without journey progress must trigger explicit reprioritization.
  This priority grants no waiver of essential checks or authority to mark an
  incomplete product accepted. Core journey evidence and full acceptance remain
  separate milestones; narrow routine fixes need no new planning ceremony.
- PJS-009: Version and hash all delivered resources, selection metadata and
  generated steering through both creation provenance records and provider
  packaging. Validate completeness, safe paths, collisions and local references
  before publication. Preserve immutable releases and no-clobber creation.
  Future updates use reviewed project diffs preserving adaptations and unknown
  skills; no global settings or installed host-policy changes.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| PJS-AC01 | Reviewed capability/reuse matrix accounts for all six capabilities; complete packages and local references work without the source checkout. | PJS-001, PJS-006–007 |
| PJS-AC02 | Isolated planning, web/static, API, Android and mixed-stack fixtures receive exactly their selected packages via both applicable creation paths. Unknown-stack creation and later explicit Android selection succeed without overwriting an adapted skill; unchanged retry makes no writes. | PJS-002, PJS-009 |
| PJS-AC03 | Behavioral Android scenarios cover ambiguous device, missing tool, upgrade with retained data, boot/launch, UI/location, interruption and bounded evidence. Fresh supported-client use on an existing reviewed Android fixture demonstrates actual skill discovery and an upgrade plus a native journey. Physical qualification remains explicitly separate. | PJS-003, PJS-005 |
| PJS-AC04 | Preview scenarios reject source/artifact/signature mismatch, unsafe uploads and unauthorized publication; a scoped non-production build/install observation records exact identity, privacy and retained app data. Live external actions need their own existing scope authorization. | PJS-004 |
| PJS-AC05 | Runtime and handover scenarios demonstrate readiness versus process state, missing interface, unknown operation outcome and stale installed artifact. A consumer can identify the current journey blocker and next action from a concise report. | PJS-006–007 |
| PJS-AC06 | Generated steering and adapted plans prioritize a runnable journey over speculative hardening. Paired behavioral scenarios show an agent defer an optional edge case, fix an observed blocker, and retain a required privacy/data-integrity gate; mock tests cannot close the journey milestone. | PJS-005, PJS-008 |
| PJS-AC07 | Missing/unsafe resources, collisions, bad references and stale provider inventory fail before publication; hash/selection provenance and packaged-provider parity pass. Relevant offline checks and CI results are recorded independently. Published releases and existing projects remain unchanged. | PJS-002, PJS-009 |

## Completion and ownership

Deliver reviewed skills, shared selection/materialization support, portable
references, generated steering, updated creation documentation, tests and sanitized
acceptance evidence. The project owner reviews the draft and implementation scope.
Mark Delivered only after merged implementation and required acceptance; pending
client/runtime checks remain pending. Installed-provider rollout uses its existing
reviewed operator path and is not implied by a merged source change.
