# SPEC-041 — Dependency automation (QLT-003)

- **Status:** Implemented — PR #95 merged; task records closed by project-owner request; remaining acceptance is tracked separately.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-003
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Generated applications receive a bounded stream of reviewable, tested dependency-update
pull requests that preserve exact toolchains, lockfiles and runtime compatibility.

Cover npm/pnpm, Python/uv and GitHub Actions where the selected updater supports the
actual lock format. Treat missing lockfile support as an explicit capability gap
requiring a reviewed adapter, not permission to switch package managers. Review majors,
runtime/profile changes and framework-coupled upgrades separately. Security updates use
the same merge gates; no auto-merge is proposed.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
The initial overnight authorization covered pushing branches and opening PRs.
The project owner subsequently authorized PR #95 merge and closure of all tasks
on 2026-10-21; PR #95 is now merged. Deployment remains excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

The root .github/dependabot.yml covers GitHub Actions and Terraform weekly with five
open PRs per ecosystem. It does not configure package updates for generated
applications. Published template releases are immutable, including their dependency
pins.

Depend on QLT-001/002 for checks, SPEC-019/020 for dependency/toolchain policy and
SPEC-021 for release immutability. Expo compatibility remains governed by the reviewed
mobile profile.

Source/previous-record evidence, not a new runtime verification:

- [.github/dependabot.yml](../../.github/dependabot.yml)
- [config/project-dependencies/v1.json](../../config/project-dependencies/v1.json)
- [config/toolchains/v1.json](../../config/toolchains/v1.json)
- [config/mobile/v1.json](../../config/mobile/v1.json)
- [scripts/project_dependencies.py](../../scripts/project_dependencies.py)
- [scripts/check-template-releases.py](../../scripts/check-template-releases.py)

## Requirements

### QLT-003-R01 — Repository coverage

Generate updater configuration for every supported ecosystem and nested component
directory with documented exclusions, cadence and a repository-wide PR cap.

### QLT-003-R02 — Bounded changes

Group compatible patch/minor updates conservatively; keep majors, exact toolchain
profiles and coupled Expo/React Native changes in explicit reviewed lanes.

### QLT-003-R03 — Tested lockfiles

Require exact direct pins where current policy requires them, coherent frozen lockfiles
and QLT-002 checks on every update before human merge.

### QLT-003-R04 — Scoped bot access

Use the native updater identity with minimal repository scope and no host/runtime
credentials; classify unavailable ecosystems, advisories or private registries as
explicit gaps.

### QLT-003-R05 — Maintenance and release integrity

Document triage, stale/failed updates, urgent security escalation and explicit pauses;
update GptClaw-owned template dependencies only through new immutable releases.

## Acceptance criteria

Criterion-by-criterion results and remaining trials are recorded in [acceptance evidence](acceptance.md). Automated implementation does not establish full owner acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-003-AC01 | Static checks enumerate every lockfile-bearing component and action workflow; a synthetic repository demonstrates scheduled/manual discovery without exceeding the proposed cap. | QLT-003-R01 |
| QLT-003-AC02 | Fixtures separate majors/profile changes; a coupled mobile update cannot merge with an inconsistent SDK graph; generated PRs describe the affected package group. | QLT-003-R02 |
| QLT-003-AC03 | A valid update restores and verifies; stale lockfile, policy-breaching pin and broken application fixtures fail; no automatic merge occurs. | QLT-003-R03 |
| QLT-003-AC04 | Configuration inspection and a synthetic run show no host/broker/tailnet secrets; unavailable registry and unsupported ecosystem cases report blocked status without broadening access. | QLT-003-R04 |
| QLT-003-AC05 | A rehearsed failed update is triaged/paused; template integrity checks reject edits to historical releases and accept a newly versioned successor. | QLT-003-R05 |

## Decisions and completion

Use weekly Dependabot with one open PR per ecosystem/component, conservative patch/minor grouping and explicit major/Expo/toolchain upgrade lanes. Do not enable auto-merge or add private registry credentials.

The project owner delegated reasonable implementation choices on 2026-10-21.
The initial scope authorized source changes, synthetic tests and PR publication.
The project owner subsequently authorized merge and closure of all tasks; PR #95
is merged. Deployment remains separately authorized.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.