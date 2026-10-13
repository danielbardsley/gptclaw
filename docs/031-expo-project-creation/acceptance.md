# ACCEPTANCE-031: Expo / React Native creation foundation

- **Status:** Implementation in review; private repositories/CI passed; final corrective-release and owner acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Spec:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md) · **Tasks:** [TASKS-031](tasks.md)
- **Implementation PR:** [#73](https://github.com/danielbardsley/gptclaw/pull/73)
- **Creation starter:** expo-react-native@1.0.0; digest `662482948e2c3b5f5ab8160cc2c23ba6ab1ba269831583e7155ac477cb2cabfa`
- **Corrected future starter:** expo-react-native@1.0.1; digest `9a22fbea9fd28966dd23439e12e1ec2812b4ae5483c918aa5ab91a9c2ac80bc8`

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed earlier; corrective release checking | Exact selection, checksum/schema/path rejection, web-default retention and historical-release immutability passed. Published 1.0.0 is unchanged; final 1.0.1 validation is in progress. |
| AC-002 | passed local/installed | Distinct mobile identities and schema-5 static configuration validate. Duplicate/malformed/dynamic/native inputs are rejected. Ordinary source edits preserve provenance. |
| AC-003 | passed local | Offline normalized generation, no command/network invocation, destination/symlink/race/concurrency/failure preservation and existing catalogue recovery tests passed. |
| AC-004 | passed local/snapshot; live checks finishing | Real cold/warm frozen preparation and exact image selection passed; SDK/policy denials and transaction/recovery/source-retention tests passed. Live target preparation/check outcomes are being recorded. |
| AC-005 | passed local/CI/snapshot; live checks finishing | Two generated apps pass all seven gates and both native-target exports; interaction/type/syntax/style defects fail. Both private repositories pass all quality gates. Live installed checks remain separate. |
| AC-006 | passed local/private | Approved broker policy/canary created two private repositories with distinct IDs, exact 1.0.0 release provenance, initial PRs and existing explicit private-dev protection waiver. Offline denial/lost-response/changed-plan/resume cases passed. |
| AC-007 | passed private CI; corrected golden checking | Both generated repositories' final-head CI passed after reviewed workflow/guidance fixes. New golden CI executes the generated workflow itself, including its checkout ownership contract. |
| AC-008 | passed source/consumer; live recovery/owner pending | Real private inventory contains both mobile rows, no service components or app URLs, explicit unsupported runtime and correct repository links. Existing app observations need a quiet-host recovery check after verification load, plus owner browser confirmation. |
| AC-009 | pending final correction/owner/merge | Core source/installed parity, rollout/rollback and platform CI passed. Corrective release final regression/CI, capable provider refresh and owner creation/edit/check confirmation remain. Implementation has not merged; MOB-001 is not Delivered. |

## Verified platform and native-source checks

Use the prepared isolated Python 3.12 environment for offline tests. Native package
commands use the reviewed rootless Node 24.21.0/pnpm 12.10.1 image, with finite
CPU/memory/PID/time bounds and no host language/native SDK package installation.

- Integrity-checked Expo metadata established Expo 57.0.28, React Native 0.86.3,
  React 19.2.3 and Router 57.0.26. TypeScript 6.0.3, Jest 30.5.2/jest-expo 57.0.6,
  React Native Testing Library 14.1.0 and ESLint 9.39.5 passed actual jobs. The
  earlier ESLint-10 trial was incompatible with the React plugin.
- Frozen installation passed with isolated pnpm layout and all install scripts
  disabled. Five exact public transitive aliases are mobile-only; no hoisted-layout
  or package-script exception was required. Protected SDK/toolchain/advisory inputs
  remain tied to the immutable release.
- Real formatter/lint/types/interaction tests, 100% counter coverage, SDK checks,
  approved advisory policy and separate iOS/Android JS/assets exports passed.
  Golden behavior/type/syntax/style defects were rejected. A debugger-only lint
  fixture was permitted by upstream rules, so the meaningful syntax defect replaced it.
- Combined platform verification initially exceeded its single 300-second job bound
  under concurrent load. Final orchestration runs serial, individually bounded
  steps under the operation lock; no resource or individual deadline was increased.
- Full repository gate on 8b62bb4 passed with exit 0: **540 cases in 699.1 seconds**.
  The corrected-release 22-case mobile suite subsequently passed in 211.691 seconds;
  final complete regression results will be recorded separately.
- Dashboard frozen install, frontend tests/types/build, actual collector socket/HTTP
  and pinned browser regressions passed, including mobile source/runtime messaging.

All four platform workflows passed on `8b62bb4785b96ff4bb79e78a6a90e63cbc7b1c61`:
[private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38455979332),
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38455979421),
[development-host validation](https://github.com/danielbardsley/gptclaw/actions/runs/38455979264)
and [federation validation](https://github.com/danielbardsley/gptclaw/actions/runs/38455979233).
Private application CI includes all five jobs. Protected infrastructure plan/apply
were skipped; no infrastructure deployment occurred. The corrective release has a
separate final check gate.

Two exact, owner-approved tooling advisory exceptions expire at the end of
October 27, America/New_York: node-forge 1.4.0 / GHSA-86w9-cpqp-85rv and braces
3.0.3 / GHSA-vfj7-8cjw-p6xm. Unexpected high/critical findings, version drift,
incomplete/unavailable audit evidence or expiry block verification. Moderate findings
remain visible. See [security review](security-review.md) for scope, approval,
mitigation and owner removal/follow-through; this is not a clean-vulnerability claim.

## Approved broker policy and actual private repositories

The project owner approved [the exact four-name scope](acceptance-targets.md) with
“Yes, all approved.” Profile 4 permits at most four explicit names, while profile 3
retains its two-name limit. Active names are exactly Shelfmark, Trailboard and the
two targets below. Existing App/installation grants and singleton token scopes
remain unchanged. Two live helpers were refreshed; two absent archived-source
bindings/helpers were preserved. Incomplete helper-upgrade journals still block.

The reviewed policy update briefly paused new credential issuance, proved the first
mobile canary's workflow publication and reactivated before creating the second app.
No wildcard, automatic enrollment, 64-name policy, PAT or Expo/signing account was
added. The earlier unapproved 64-name command was rejected and did not run; the
smaller exact scope was subsequently authorized and applied.

| Target | Repository ID | Initial app PR | Final corrected head | Quality CI |
|---|---|---|---|---|
| mob001-accept-one | 1417864877 | [#1](https://github.com/danielbardsley/mob001-accept-one/pull/1) | `3e90ca75f579935cef58815b390d7644dd15a96b` | [passed](https://github.com/danielbardsley/mob001-accept-one/actions/runs/38459224503) |
| mob001-accept-two | 1417867323 | [#1](https://github.com/danielbardsley/mob001-accept-two/pull/1) | `be73a6963b394b7e1d490beb8af991307d5e9477` | [passed](https://github.com/danielbardsley/mob001-accept-two/actions/runs/38459243651) |

Both were created from immutable 1.0.0. Their first actual CI exposed the Docker
image user's mismatch with GitHub's checkout owner. Managed format-check also found
an extra blank line in broker-adapted AGENTS.md. Reviewed ordinary source commits
fix the workflow UID/GID and guidance on their existing initial PR branches. Original
creation provenance and protected policy inputs are retained. New release 1.0.1
carries the workflow fix for future explicit creation; it does not rewrite 1.0.0.

Both final private CI jobs passed toolchain build, frozen install and complete
formatter/lint/type/interaction/SDK/security/iOS-and-Android export verification.
The existing explicit unprotected-private-dev waiver applies; no server enforcement
claim or automatic initial-PR merge is made. Sources and PRs are retained for review.

## Installed provider, dashboard and rollback

Core stable provider **1.10.1** uses immutable snapshot
`54e90ac2d178f1972a455ec54a93594afc472cb77c2130c0c0423b28620605cf`.
Dashboard release is
`24ab5773f969a5a02582660124b93de2bc0fee198806d58351d53a847d7aebd2`.
Its collector uses the capable frozen provider. Both updates used reviewed owned
interfaces; AWS, host policy, grants and Tailscale configuration were not changed.

The actual private HTTPS health/snapshot return 200. Metadata adds only both exact
mobile root/ID/owner/repository entries and retains existing registry entries.
Inventory contains four rows: two existing groups and two native source projects.
Mobile rows have no components, runtime observation or app URL; repository links
match their actual private destinations. Verification load can cause bounded
observations to become stale/degraded; quiet-host recovery must be recorded before
claiming current ready observations for existing projects.

Earlier owned provider/dashboard rollback restored provider 1.9.0 and dashboard
`d0485098d81d573b41943793b91a39b03f8a509bbfb22c3aa261ef3e64d803d1`,
then restored the capable releases. Older-provider mobile rejection preserved source.
Profile 4 now requires a compatible provider; retain it or restore the previous
reviewed policy through its typed interface before selecting an older provider.
Reconcile unresolved mobile jobs with a capable snapshot first. Rollback does not
undo app commits, dependencies or private repository creation.

Shelfmark/Trailboard source, six app/API/DB containers and persistent data remain
outside acceptance fixture operations. Existing /projects/ and /dashboard/ private
Serve handlers remain present and Funnel is off. No mobile Metro/application service,
EAS project, signed native binary, device session or public exposure was created.
Intentional synthetic counter/about content remains for starter acceptance; product
adaptation must review/remove unwanted demos and test actual product behavior.

## Remaining delivery

Complete corrected release/platform regression and CI, installed target checks,
capable provider/collector refresh, quiet-host observation recovery and owner
creation/edit/check/browser confirmation. Obtain the separate implementation merge
disposition before merging #73. Keep source/private PRs and task-owned evidence for
review; no incidental repository/source/data deletion. Mark only MOB-001 Delivered
after merged implementation and AC-001–009 pass. TPL-004 device acceptance and mobile
M1–M4 remain separate.
