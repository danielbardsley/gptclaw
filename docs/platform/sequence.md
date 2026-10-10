# GptClaw feature delivery sequence

- **Status:** Recommended delivery order; not implementation authorization
- **Owner:** Daniel
- **Last updated:** 2026-10-10 (America/New_York)
- **Feature definitions and current status:** [Feature catalogue](./features.md)
- **Architecture:** [Platform architecture](./architecture.md)

## Goal and sequencing rules

Deliver a usable private development platform first. **Daniel's current direction
keeps remaining RES work deferred until a useful real application exists.** The
accepted Hello World/two-app workflow demonstrates the initial technical path;
it does not by itself end this owner-directed deferral. Milestone U remains a
technical prerequisite for later resilience work, not an automatic start signal.
Existing snapshots, deletion protection, private access, and data safeguards
remain in place. This deferral does not claim recovery has been tested or close
outstanding acceptance, exceptions, or owner follow-through.

This file sequences every current catalogue feature, including already delivered
foundations and optional work. It refines the catalogue's broad suggested order
for Daniel's working-platform-first preference. Feature IDs and catalogue
priorities are not execution order. The catalogue remains the source for status;
this document does not mark any feature complete.

Work through numbered stages in order. Within a stage, follow the table from top
to bottom; features grouped in a row form a coherent delivery group. Design
coupled interfaces together, then implement their providers before consumers.
Independent work can overlap once its prerequisites exist. Later product tracks
can be reordered when needed, retaining their stated dependency gates.

Each selected group still needs a specification, technical design, tasks, and
observable acceptance. A stage can contain several initiatives and PRs. Host
changes use committed code and the existing protected infrastructure pipeline;
a request to sequence work does not authorize installing or deploying it.

Where a feature is introduced in a limited form, its later expansion is named
below and in the completion ledger. Keep its overall catalogue status incomplete
until the full accepted scope is delivered, or explicitly revise the scope and
record follow-up ownership. A mock runtime or command stub is not live acceptance.

## 0. Reuse the delivered foundation and existing agent guidance

| Features | Treatment |
|---|---|
| FND-001, FND-002, FND-003, FND-004, FND-005, FND-006 — host, volume, private access, remote connection, repository credential, workload identity | Existing delivered baseline; do not rebuild. The current repository credential does not authorize access to new project repositories. |
| RES-001 — automated EBS snapshots | Existing delivered backup capability stays enabled. Remaining RES features start only after stage 6. |
| AGT-001, AGT-002, AGT-003 — host, repository, and nested guidance | Reuse installed/merged guidance. Capture remaining applicable fresh-session checks during normal work; defer host-replacement-dependent acceptance to stage 7. |
| AGT-004, AGT-005 — specification and bootstrap skills | Use for planning and the existing planning-only starter; finish relevant client acceptance when exercised. The starter is not yet a runnable application template. |
| AGT-008, AGT-009, AGT-010 — handover, decisions, context validation | Reuse during subsequent initiatives; resolve their recorded acceptance and owner decisions through their own tasks. Do not repeat their implementation. |

AGT-006's live runtime acceptance belongs in stage 6. AGT-007's release rehearsal
belongs in stage 15, when a reviewed product pipeline exists. Existing acceptance
records remain authoritative; this schedule does not erase pending checks.

## 1. Finish the shared project contract

| Features | Delivery and exit evidence |
|---|---|
| PRJ-001 — versioned project manifest | Finish review, merge, and acceptance of the manifest/schema/validator work already underway. Prove offline validation and useful rejection errors. |

The initial contract is one web service with no platform-managed persistent
application data. Later quality commands, toolchain declarations, permissions,
multiple services, secrets, and publication may require explicit versioned
contract extensions. Do not silently put unsupported fields into version 1.

## 2. Install the minimum supported execution environment

| Features | Delivery and exit evidence |
|---|---|
| SYS-004, SYS-001 — host tool profile and rootless container toolchain | Define the reviewed installation/update path, then deliver Podman, subordinate IDs, networking, storage, Quadlet, and user-service persistence. Prove the actual host supports a rootless disposable container and persistent user services. |
| SYS-003 — project dependency policy | [Delivered SPEC-019 initial adapter](../019-project-dependency-policy/acceptance.md): project/container installation boundaries, typed pnpm dependency changes, lockfile review and recovery. Reuses SPEC-018’s reviewed container baseline; local/live checks, CI and owner acceptance are recorded and implementation is merged. |
| SYS-002 — pinned language toolchains, initial web slice | [Delivered SPEC-020 initial web slice](../020-pinned-language-toolchains/acceptance.md): extends SPEC-018's working fixed Node/pnpm pair with exact per-project selection, verified acquisition, a supported matrix and legacy compatibility. Integrates the delivered SYS-003 policy for automatic dependency use. Python/uv and additional stacks follow in stage 12. |

**Current stage-2 follow-up:** Daniel requested separate SYS-003 and SYS-002 plans
on October 10. SPEC-019 reused the reviewed container/toolchain; its initial
pnpm adapter passed local/live checks and CI, was accepted by Daniel and merged
in PR #46. SPEC-020 consumes its delivered policy for lifecycle preparation. Its
initial web slice passed local/live checks and configured CI, was accepted by
Daniel and merged in PR #48. Later profiles/languages remain separate reviewed
work. Do not reinstall the already
deployed SYS-001/SYS-004 foundation or invalidate their separate acceptance.

## 3. Deliver the runtime that the CLI will control

| Features | Delivery and exit evidence |
|---|---|
| SEC-003, RUN-001, RUN-004 — permission profiles, rootless project isolation, resource limits | Establish a restricted web-project execution profile, then enforce isolation and bounded CPU, memory, processes, storage, and logs. Test denial and cross-project isolation, not just container startup. Expand profiles when later capabilities require it. |
| RUN-003, RUN-005 — port registry and health contract | Define port ownership, allocation/release/recovery, startup/readiness checks, timeouts, and state meanings before lifecycle integration. |
| OBS-001, SEC-006 — structured logging and audit | Define redacted logs and operation correlation/results for runtime consumers. Start with lifecycle events; later adapters add their own events using the same contract. |
| RUN-002 — user systemd/Quadlet lifecycle | Implement the reviewed lifecycle backend using those contracts. Verify start, stop, restart, disconnect survival, health failures, busy operations, and interrupted-operation reconciliation. |

Accept this stage against disposable services through the documented backend
interface. Prove two projects receive separate ports and limits and can start or
stop independently. PRJ-002 will call this backend; it must not implement a second
competing lifecycle system. Runtime-generated state stays outside source manifests.

## 4. Build one usable web template

| Features | Delivery and exit evidence |
|---|---|
| QLT-001, QLT-002, SEC-005 — quality commands, PR workflow template, secret scanning | Define the template's standard checks, language-specific coding style guides, and pinned CI workflow, with an explicit manifest extension where required. Deliver TypeScript/JavaScript conventions for formatting, naming, code organization, and idiomatic usage; encode enforceable rules in formatter/linter configuration and document explanatory conventions in template guidance. Verify the generated configuration and checks in a synthetic project, including rejection of representative style violations. Live new-repository provisioning follows in stage 9. |
| PRJ-003 — template catalogue, first-entry slice | [SPEC-021](../021-template-catalogue/spec.md) implements: versioned discovery, exact release selection and provenance for the existing supported web starter. Initial scope approved and implementation authorized October 10; implemented/local/live verified in provider 1.3.0, all three implementation CI workflows passed, review/acceptance/merge pending. Broader template coverage follows in stages 12 and 16. |
| TPL-001, NET-103 — Next.js template and base-path compatibility | Deliver an actual buildable/testable web app, container definition, health route, and working assets/API/redirect behavior beneath its project path. Use the stage 3 runtime; complete route acceptance in stage 5. |
| PRJ-009 — example projects, first web slice | Maintain a non-sensitive example that exercises the supported template. Add examples whenever later templates are introduced. |

The first app has no managed database or runtime secrets. Creating local projects
is enough for the first milestone; automatic GitHub repository creation is later.

## 5. Open the app privately and prove its update loop

| Features | Delivery and exit evidence |
|---|---|
| NET-101, NET-102 — loopback ingress and Tailscale Serve manager | Deliver healthy-service routing and recoverable private Serve configuration. Verify access from an authorized tailnet client with no public listener or Funnel. |
| NET-108 — preview URL registry, private slice | Record real private routes and return their stable URLs. Public URL/expiry entries follow in stage 13. |
| QLT-004 — preview smoke tests | Test the private URL, assets, health route, and a useful journey after an app change. Finish TPL-001/NET-103 acceptance against real ingress. |
| SEC-007, QLT-009 — destructive-action controls and golden-template tests, initial slices | Define explicit disposable targets and safe cleanup before automating generate/build/run/route/teardown tests. Initial cleanup applies only to owned ephemeral fixtures; persistent-data and archive operations follow in stage 10. |

## 6. Deliver the operational CLI and reach the usable-platform milestone

| Features | Delivery and exit evidence |
|---|---|
| PRJ-006 — branch/worktree policy | Define branch/worktree identity, per-project operation locks, and handoff behavior before CLI project creation and concurrent operations. Reuse runtime locking rather than adding incompatible ownership rules. |
| PRJ-002 — CLI, first operational release | Integrate local `new`, `validate`, `start`, `stop`, `restart`, `status`, bounded `logs`, and `test` with the proven template, validator, and backend. Define the supported build/update operation, human/JSON results, timeouts, and reconciliation. Return the private URL after readiness. |
| AGT-006 — runtime-operation skill live acceptance | Bind the skill to the actual versioned CLI contract and complete status/log/start/restart/stop acceptance on a disposable managed service. |

**Milestone U — usable private platform:** from a fresh supported client session,
create a local web project, validate/build/test it, start it, open its private URL,
request a code change, apply the supported update workflow, and observe the change.
Read logs/status, restart, and stop it. Repeat with a second independently running
project; changing or stopping one must not disrupt the other. Record revisions,
actual commands, health/routing evidence, and remaining limitations.

A dashboard, automated GitHub creation, databases, mobile support, public exposure,
and production deployment are not required for this milestone. Neither is any
remaining RES feature. **Stage 7 requires Milestone U and Daniel's useful-application gate stated above.**

PRJ-002 remains responsible for subsequent integrations: repository provisioning
in stage 9, archive/restore in stage 10, and public `expose` in stage 13. Its first
release must explicitly document these exclusions rather than report the full
catalogue feature Delivered. If `expose` is defined as private-route management,
accept that meaning here and specify public exposure separately in stage 13.

## 7. Resume resilience work after the platform is usable

| Features | Delivery and exit evidence |
|---|---|
| RES-002 — restore drill | Prove an existing recovery point can restore to an inspectable replacement volume without changing the live volume. |
| RES-006 — disk capacity guardrails | Add warning and build-admission thresholds. Establish cleanup rules; integrate automated cache/runtime pruning after stage 8 providers exist. |
| RES-003 — backup freshness indicator | Deliver the freshness/retention/restore-result data source and a usable CLI or report view; dashboard integration is stage 11. |
| RES-005 — host configuration drift detection | Compare the now-real host tool profile and runtime configuration with observed state. |
| RES-004 — host replacement rehearsal | Exercise the accumulated host/runtime setup, volume recovery, private access, credentials, and reauthentication. Close applicable AGT-001 replacement/bootstrap acceptance with actual evidence. |
| RES-007 — platform export (optional) | Add non-secret inventory and recovery exports only if requested; refresh when stage 9 discovery is available. |

Do not relabel these as SYS/RUN prerequisites to pull them ahead of Milestone U.
Deferral leaves restore/replacement evidence outstanding until this stage runs.

## 8. Make everyday operations sustainable

| Features | Delivery and exit evidence |
|---|---|
| OBS-002, OBS-005 — metrics and retention | Collect host/project health and resource signals; bound retained logs, audit, builds, images, and artifacts. |
| SYS-006, RUN-010 — dependency caches and runtime garbage collection | Add quota-controlled caches and safe orphan cleanup under SEC-007 controls. Integrate RES-006 disk guardrails. |
| RUN-009, RUN-008 — build queue and idle lifecycle | Bound concurrent builds, then add supported pause/resume/idle shutdown with reliable state and URL preservation. Extend the CLI and its tests. |
| OBS-006, OBS-003 — service history and alert routing | Preserve availability/change history and route actionable health, disk, backup, restart, and deployment alerts. Use an approved destination; Slack is not a dependency. |
| SYS-007, SEC-004, QLT-003 — SBOMs, scanning, dependency automation | Produce component inventories, scan dependencies/images with an actionable policy, and open bounded tested updates. |
| OPS-004 — platform upgrade workflow | Rehearse staged upgrades with health checks and rollback using the delivered profile, recovery, and runtime capabilities. |
| OPS-001 — cost dashboard | Establish cost data and budget thresholds; integrate its platform UI in stage 11. |

## 9. Automate repository creation and project inventory

| Features | Delivery and exit evidence |
|---|---|
| SEC-001, SEC-002 — secret registry and rotation | Establish scoped secret materialization outside Git and a tested rotation/health/audit workflow before adding project credentials or services that need secrets. |
| PRJ-005 — repository credential broker | Provide narrow per-repository credentials and lifecycle/rotation using the established secret boundary. |
| PRJ-004 — new GitHub repository automation | Create repositories, protections, environments, secret references, and initial PRs with brokered credentials and stage 4 workflow templates. Extend PRJ-002 `new`; retain a local-only mode. |
| PRJ-007 — project discovery | Discover validated project metadata without executing it. Supply inventory for dashboards, export, and targeted operations. |

## 10. Add persistent data and richer project lifecycles

| Features | Delivery and exit evidence |
|---|---|
| RUN-006 — multi-service projects | Extend the manifest and runtime contract explicitly for component identity, dependency order, networking, health, and scoped operations. |
| QLT-007, RUN-011 — migration gates and development databases | Define migration/backup/restore gates, then deliver isolated databases, roles, credentials, and controlled reset. Requires stage 7 recovery evidence and stage 9 secret handling. |
| RUN-012 — synthetic seed data | Provide reproducible non-sensitive seed/reset operations under the database and destructive-action contracts. |
| RUN-007 — background jobs and schedulers | Add managed workers/jobs with limits, logs, status, and supported scheduling. |
| PRJ-008 — project archive and restore | Specify data retention/export/restore, previews, and recovery before archive mutations. Finish the persistent-data portion of SEC-007 and integrate PRJ-002 archive/restore with real recovery tests. |

## 11. Deliver the platform dashboard over proven interfaces

| Features | Delivery and exit evidence |
|---|---|
| TPL-008, QLT-005 — UI foundation and accessibility | Establish reusable accessible UI conventions and checks; apply them to the dashboard and supported templates. |
| DSH-001, DSH-002, DSH-003, DSH-004, DSH-014 — inventory, status, links, Git state, degraded mode | Deliver the read-only dashboard over discovery/runtime/route interfaces; handle unavailable backends explicitly. |
| DSH-005, DSH-006, DSH-007, DSH-008, DSH-011 — telemetry, logs, checks, backup state, audit timeline | Integrate existing metrics, redacted logs, build results, RES-003 recovery data, and audit events. Include OPS-001 cost views. |
| DSH-013, DSH-012 — search and mobile-friendly layout | Make the populated dashboard navigable and usable from a phone over the tailnet. |
| DSH-009 — constrained controls | Add reviewed typed runtime actions only after read-only state and the CLI/backend are reliable. Verify permissions, exact targets, and operation results. |

## 12. Expand supported templates and mobile development

| Features | Delivery and exit evidence |
|---|---|
| NET-104 — dedicated private service ports | Add the private routing alternative for frameworks that cannot safely use a base path. |
| QLT-008, TPL-002, TPL-003, TPL-005 — API contracts, TypeScript API, Python API, static site | Deliver these stacks with their required toolchains, tests, health, data/migration support where relevant, and private routing. Finish SYS-002 Python/uv support and update PRJ-003/PRJ-009/QLT-009 for each stack. |
| TPL-009, TPL-010 — authentication and AI starters | Build on scoped secrets, rotation, supported data services, and existing quality checks. Use synthetic identities/data for acceptance. |
| QLT-006 — performance budgets | Establish measured build, response, resource, and startup budgets for supported templates. |
| MOB-005, TPL-004 — mobile environment profiles and Expo template | Separate configuration/credentials first, then introduce Expo and its pinned tools with explicit native/web runtime behavior. |
| MOB-001, MOB-002, MOB-003, MOB-008 — creation, device access, Expo Go, web preview | Integrate Expo project creation, private device connectivity, compatible Expo Go iteration, and universal web previews. |
| MOB-004 — development builds | Add signed development builds when native modules require them; prove credential handling and artifact access. Store submissions remain stage 15. |
| MOB-009 — mobile dashboard state, development slice | Show Metro sessions, device links, and development build jobs. Release/channel views finish in stage 15. |

Every newly supported stack extends SYS-002 as needed and receives versioned
PRJ-003 registration, PRJ-009 examples, and QLT-009 generate/run/route/cleanup tests.
Each newly supported language also receives a coding style guide and applicable
formatter/linter configuration following the stage 4 baseline, with conventions
in template guidance and representative style violations checked in tests.
These are explicit continuing obligations, not assumed coverage from one web app.

## 13. Add controlled public previews

| Features | Delivery and exit evidence |
|---|---|
| SEC-009, NET-109 — tailnet policy as code and access groups | Establish reviewed developer/viewer/service access before expanding audiences or enabling public publication controls. |
| SEC-010 — security review workflow | Review the proposed publication boundary before enabling it; reuse the workflow again for production in stage 15. |
| NET-107, NET-106 — exposure scanning and authentication | Block unsuitable endpoints and require the selected authentication/share-token model before publishing an app that needs it. |
| NET-105 — Funnel exposure manager | Deliver explicitly authorized, health-gated, expiring public previews with audit and verified shutdown. Extend NET-108 public URL/expiry records and PRJ-002 public `expose`. |
| DSH-010 — Funnel dashboard controls | Add controls over the proven exposure contract, including expiry and revocation status. |

Reconcile PRJ-002's full accepted command scope here: runtime and local creation
(stage 6), GitHub creation if selected (stage 9), archive/restore (stage 10), and
public exposure (this stage). Finish remaining acceptance before marking it Delivered.

## 14. Add Slack collaboration

| Features | Delivery and exit evidence |
|---|---|
| COL-008 — official integration evaluation | Evaluate current official capabilities first; decide which custom features are still needed without assuming an integration satisfies platform controls. |
| COL-007, COL-003 — Slack security boundary and identity mapping | Define authentication, project scope, replay protection, channel restrictions, and secret handling before inbound operations. |
| COL-001 — notifications | Connect audited events/alerts to approved destinations with appropriate filtering. |
| COL-004, COL-002 — approval workflow and command adapter | Tie approvals to exact operations, then expose typed commands through the reviewed backend; never grant a shell. |
| COL-005, COL-006 — task bridge and progress summaries | Create traceable scoped tasks and rate-limited updates linked to authoritative work and diffs. |

Slack is an optional product adoption decision even though its catalogue entries
are candidates. It is not a prerequisite for local development or production.

## 15. Add product-specific production and mobile releases

| Features | Delivery and exit evidence |
|---|---|
| PRD-001, SEC-008 — production architecture and credential isolation | Select each product's deployment/data/recovery design and isolate production identities from development processes. Apply SEC-010 review before launch. |
| PRD-002 — per-project HCP workspace | Deliver isolated state, workload identities, environment gates, and drift visibility through reviewed infrastructure. |
| PRD-003 — immutable artifact build and registry | Build, scan, attest, and retain artifacts for promotion without rebuilding between environments. |
| PRD-006, PRD-005, PRD-007 — production secrets, domains/TLS, databases | Provision the product's required services through its protected pipeline. Database deployment is conditional on product need and requires migration/recovery gates. |
| PRD-008, PRD-009 — rollback/roll-forward and smoke tests | Implement and rehearse recovery plus health/journey checks before enabling production promotion. |
| PRD-004, AGT-007 — environment promotion and release-skill acceptance | Deliver the reviewed promotion interface, rehearse it in isolated non-production, and complete the skill's pending live acceptance. Actual production promotion requires its own concrete authorization. |
| MOB-006, MOB-007 — EAS Build/Submit and Update policy | For mobile products, deliver signed release artifacts, approved submissions, runtime/channel compatibility, rollout, and rollback using the mobile credential/environment boundaries. This track can proceed independently of unneeded AWS product resources. |
| MOB-009 — release dashboard completion | Add channels, submitted/released versions, and release-job state to the existing development views. |
| PRD-010 — production incident mode (deferred) | Consider only after a concrete production operating need exists; define time-bounded audited access without standing developer production administration. |

## 16. Demand-driven capabilities after their prerequisites

These are placed last to keep the initial platform focused. Select one earlier
only for a real use case and after its prerequisites are accepted. Optional
catalogue entries remain optional; this file does not make them mandatory.

| Features | Earliest sensible dependency point |
|---|---|
| SYS-005 — privileged capability broker | After the host profile, audit, and destructive-action controls; only for a named capability not handled by the reviewed pipeline. It is not a prerequisite for SYS-001 installation. |
| PRJ-010 — repository ownership transfer (optional) | After credential brokerage, rotation, repository automation, archive/recovery, and an actual transfer need. |
| TPL-006, TPL-007 — CLI/automation and multi-package templates (optional) | After applicable toolchains/runtime/jobs and template testing exist. Extend PRJ-003, PRJ-009, and QLT-009 when adopted. |
| QLT-010 — release notes/changelog (optional) | Once a product has an accepted release workflow and readers who need release summaries. |
| OBS-004 — trace correlation (optional) | After structured logs and multi-service behavior justify distributed tracing. |
| OPS-003 — capacity recommendations (optional) | After enough metrics and cost history exist to make useful recommendations. |
| OPS-002 — host schedule (optional) | Only after reliable remote wake-up is separately specified and proven, recovery is rehearsed, and running projects can be handled safely. |

## Completion ledger for features delivered in slices

| Feature or group | First usable slice | Explicit later responsibility |
|---|---|---|
| SYS-002 | Stage 2: SPEC-018 fixed Node/pnpm baseline; SPEC-020 adds project selection/matrix/verification | Stage 12: Python/uv and Expo needs; stage 16: additional selected stacks. Extend SYS-003 adapters and the supported-version matrix with each adopted stack. |
| SEC-003, SEC-006, OBS-001 | Stage 3: runtime permissions, audit, logs | Each later service/adapter extends and tests these contracts before use; full accepted scope governs completion. |
| PRJ-003, PRJ-009, QLT-009 | Stages 4–5: first web template and example/tests | Stage 12: additional candidate stacks; stage 16: optional stacks only when selected. Keep unsupported templates explicit. |
| TPL-001, NET-103 | Stage 4: runnable template/base-path behavior | Stage 5: actual private-ingress acceptance. |
| SEC-007 | Stage 5: ephemeral fixture cleanup | Stage 8: pruning; stage 10: persistent data, reset, archive, and restore. |
| PRJ-002 | Stage 6: operational local web workflow | Stage 9: repository integration; stage 10: archive/restore; stage 13: public exposure and full command-scope acceptance. |
| NET-108 | Stage 5: private URLs | Stage 13: public URL and expiry integration. |
| RES-003, OPS-001 | Stages 7–8: recovery/cost sources and initial views | Stage 11: integrated platform dashboard. |
| RES-006 | Stage 7: disk guardrails | Stage 8: safe cache/runtime pruning integration. |
| MOB-009 | Stage 12: development state | Stage 15: release/channel state. |
| AGT-001, AGT-006, AGT-007 | Existing merged guidance/skills | Stage 7: replacement-related acceptance; stage 6: runtime live acceptance; stage 15: release rehearsal, respectively. |

When selecting the next initiative, record which rows and slices it closes,
which dependencies were actually verified, and which later tasks remain. Update
this sequence when dependencies or owner priorities change, and update catalogue
status only from the corresponding merged implementation and acceptance evidence.
