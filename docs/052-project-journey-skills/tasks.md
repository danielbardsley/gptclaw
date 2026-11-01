# Tasks: Project skills and working application journeys

Status: Implementation authorized November 1, 2026; verification in progress. Owner: project owner.
Date: November 1, 2026. [Specification](spec.md) · [Design](technical-design.md).

## Planning and authorization

- [x] PJS-P01: Inspect current creation inventory, existing skills and SPEC-050;
  review Dogstats native journey evidence without changing Dogstats.
- [x] PJS-P02: Draft requirements, applicability/reuse matrix, design, tasks and
  measurable acceptance; add documentation index and catalogue entry.
- [x] PJS-P03: Project owner approved the draft and requested implementation
  on November 1, 2026. Installed-provider rollout and existing-project adoption
  remain outside this authorization.

## Implementation in dependency order

- [x] PJS-T01: Confirm SPEC-050 merged base and inspect all current creation
  interfaces. Finalize bounded skill/resource inventory, capability mapping and
  exact versioned selection/materialization contract. PJS-001–002/009; AC01–02/07.
- [x] PJS-T02: Reuse specification, runtime-operation and session-handover;
  preserve current consumers, remove downstream dependencies on the source
  checkout, and add acceptance reconciliation. Create Android operation, native
  preview and journey verification packages with complete checklists/assets.
  PJS-001/003–007; AC01/03–05.
- [x] PJS-T03: Implement deterministic selection in both planning and catalogue
  creation, including unknown-stack and mixed-stack behavior, standalone later
  materialization, safe no-op/collision handling, immutable reads, package
  closure, hashes and provider packaging. Update exact command documentation
  and bootstrap skill. PJS-002/009; AC02/07. Depends on T01–02.
- [x] PJS-T04: Add delivery steering to the versioned local engineering bundle,
  require it from generated root guidance and reinforce it in planning outlines
  and journey skill. Define a principal journey, first demonstration milestone,
  deferred work/revisit triggers and protected essential gates. PJS-005/008;
  AC06. Depends on T01; coordinate with T02–03.

## Verification and delivery

- [ ] PJS-T05: Add/run selection, complete-package, safe-path, link, provenance,
  collision, retry and provider-parity regressions across both creators and all
  supported families. Review paired behavioral skill scenarios, including
  speculative-edge-case deferral versus actual privacy/data-loss blockers.
  Run relevant focused and offline repository checks and generated-output
  quality gates; record exact outcomes. All requirements; AC01–07.
- [ ] PJS-T06: In an authorized existing non-production Android fixture, verify
  fresh-client discovery and actual use: exact build/upgrade with retained data,
  real native journey and persisted result, scoped interruption checks and
  concise evidence reconciliation. Preserve data; no host provisioning, cloud
  uploads or physical qualification implied. Record missing prerequisites as
  pending. PJS-003–008; AC03–06. Depends on T02–05.
- [ ] PJS-T07: Record sanitized acceptance by criterion with revision, local/CI/
  runtime/client distinctions and limitations; deliver reviewed implementation
  PR, track merge and any separately authorized installed-provider rollout.
  Update catalogue honestly and preserve existing projects/releases. All
  requirements; AC01–07. Depends on T05; T06 acceptance may remain pending.

## Current handover

The principal delivery journey is implemented: generate a project with common
skills, preview applicable additions, apply them from its own recorded offline
bundle, and retry without writes. Skills, steering and selection support are
source changes only; no installed provider or existing project was changed.
SPEC-050 is merged in PR #107; this branch is based on main 07e66ab. The draft
initiative 051 is now 052 because main already used 051 for the Android runner.
See [acceptance evidence](acceptance.md) for actual checks and pending client/
Android/runtime observations. No host provisioning or cloud upload was performed.
