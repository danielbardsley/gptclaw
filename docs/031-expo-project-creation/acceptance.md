# ACCEPTANCE-031: Expo / React Native creation foundation

- **Status:** Delivered — merged implementation and owner acceptance complete
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Spec:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md) · **Tasks:** [TASKS-031](tasks.md)
- **Implementation PR:** [#73](https://github.com/danielbardsley/gptclaw/pull/73) — merged as `f40a7f33f6ba8a1f1880b10463cace88f6d88a45`
- **Creation starter:** expo-react-native@1.0.0; digest `662482948e2c3b5f5ab8160cc2c23ba6ab1ba269831583e7155ac477cb2cabfa`
- **Corrected future starter:** expo-react-native@1.0.1; digest `9a22fbea9fd28966dd23439e12e1ec2812b4ae5483c918aa5ab91a9c2ac80bc8`

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed local/CI/installed | Exact selection, checksum/schema/path rejection, historical immutability and web-default retention passed. Both releases remain valid; installed 1.0.1 discovery and two offline creations/validations passed with exact digest. |
| AC-002 | passed local/installed | Distinct mobile identities and schema-5 static configuration validate. Duplicate/malformed/dynamic/native inputs are rejected. Ordinary source edits preserve provenance. |
| AC-003 | passed local | Offline normalized generation, no command/network invocation, destination/symlink/race/concurrency/failure preservation and existing catalogue recovery tests passed. |
| AC-004 | passed local/CI/installed | Cold/warm frozen preparation, exact image, SDK/policy denials and transaction/recovery/source-retention tests passed. Both live installations preserved package/lock/workspace hashes; complete managed checks passed. |
| AC-005 | passed local/CI/installed | Two generated apps and both private targets pass all seven gates and iOS/Android JS/assets export. Representative behavior/type/syntax/style defects fail. Live installed verification passed for both targets; no device/binary claim. |
| AC-006 | passed local/private | Approved broker policy/canary created two private repositories with distinct IDs, exact 1.0.0 release provenance, initial PRs and existing explicit private-dev protection waiver. Offline denial/lost-response/changed-plan/resume cases passed. |
| AC-007 | passed platform/private CI | Both generated repositories pass final-head CI after reviewed source fixes. Corrected golden CI executes the actual generated workflow with production-adapted guidance; all native checks/exports and defect gates pass. |
| AC-008 | passed source/consumer/private | Final HTTPS snapshot contains four current source rows; both groups are Ready/current and both mobile rows have no components/app URL, honest runtime unavailability and correct repository links. Existing app/API-doc HTTP destinations return 200. Mobile lifecycle denials preserve owned units. |
| AC-009 | passed local/CI/installed/owner | Full regression, configured CI, source/installed parity, refresh and rollback/restoration passed. Implementation merged in PR #73. On October 13 the project owner replied “Confirmed” to dashboard link/runtime-message and source creation/edit/check acceptance. This is owner-reported browser/workflow acceptance, not device acceptance. |

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
  Corrected-release focused mobile (22 cases, 211.691 seconds), repository (43 cases,
  301.314 seconds) and immutability checks passed. The final complete gate on
  implementation 528a883 passed **540 cases / 29 suites, exit 0, 841.8 seconds**.
- Dashboard frozen install, frontend tests/types/build, actual collector socket/HTTP
  and pinned browser regressions passed, including mobile source/runtime messaging.

All four platform workflows passed on implementation
`528a883524824af18715450130b99f5b40a774da`:
[private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38460331577),
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38460331790),
[development-host validation](https://github.com/danielbardsley/gptclaw/actions/runs/38460331532)
and [federation validation](https://github.com/danielbardsley/gptclaw/actions/runs/38460331583).
Application CI includes all five jobs, including actual generated-workflow execution
and both native-target exports with broker-adapted guidance. Protected infrastructure
plan/apply were skipped; no infrastructure deployment occurred. Subsequent delivery
record edits are documentation only; their branch-head checks are tracked by PR #73.

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

Final stable provider **1.10.1** uses immutable snapshot
`48a1131521aae5c2e6671faec8b3a1701c56976de6a3099f1d1d0887a4f5a5ba`.
Final dashboard release is
`73cb3c7c7c38fc667090b5226e35bd359efc034242fc30b94ea8aa399a645420`.
Its collector uses the same capable provider. Both updates used reviewed owned
interfaces after all implementation checks passed. AWS, host policy, App grants and
Tailscale configuration were unchanged. Exact stable 1.0.1 discovery, two offline
1.0.1 source creations and validation passed; both original managed 1.0.0 source
contracts validate under the final stable provider.

Both live target frozen installs preserved package/lock/workspace hashes. Complete
installed verification passed in **324.533 seconds** for mob001-accept-one and
**335.228 seconds** for mob001-accept-two, as serial individually bounded steps.
These are total command durations, not increased individual job limits. Existing
quality/dependency code is unchanged in the corrective snapshot. Managed start,
stop, restart, observe and logs all reject mobile with `mobile-unsupported`; the nine
owned unit files remained identical.

Actual final private HTTPS health/snapshot return 200; inventory is current and
complete with four rows. Both existing groups are Ready/current after verification
load subsided. The two native rows have empty components, unavailable runtime and
exact repository links. Both existing private app routes and Trailboard API-doc
route return 200. Existing registry entries were preserved while adding only the
two approved mobile entries.

Refresh, compatible rollback and restoration passed. Rollback selected provider
`54e90ac2d178f1972a455ec54a93594afc472cb77c2130c0c0423b28620605cf`
and dashboard
`24ab5773f969a5a02582660124b93de2bc0fee198806d58351d53a847d7aebd2`,
both compatible with active profile 4. Private dashboard health returned 200 at
each step; all six existing application/API/database container IDs remained
identical. The final active profile remains schema 4, active/workflow-verified,
with the exact four approved names. An initial rollout preflight matched display
names too literally and stopped before any mutation; matching the reviewed hashed
group identities corrected that inventory check.

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

## Delivery and owner acceptance

Implementation PR #73 merged into main as `f40a7f33f6ba8a1f1880b10463cace88f6d88a45`
with explicit project-owner merge approval. Its final head
`41ebb4513e00662cce3e85e8cc204b71cb2b78b9` passed all four workflows:
[applications](https://github.com/danielbardsley/gptclaw/actions/runs/38463489249),
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38463489284),
[development host](https://github.com/danielbardsley/gptclaw/actions/runs/38463489227)
and [federation](https://github.com/danielbardsley/gptclaw/actions/runs/38463489278).

On October 13, after being asked to confirm both mobile dashboard rows' runtime
unavailability and working repository links, and acceptance of the Expo/React Native
source creation/editing/checking workflow, the project owner replied **“Confirmed.”**
This is owner-reported browser/workflow evidence. AC-001–009 and T-000–012 are complete;
MOB-001 is Delivered. No phone loading, native-device or signed-build acceptance is
inferred. TPL-004's full device scope and mobile M1–M4 remain follow-ups.

Both private starter PRs and source are retained for owner inspection; the original
main checkout and untracked `.verification/` artifacts are preserved. Finite source
jobs completed; no mobile Metro/application service remains running. There is no
automatic source/repository/data deletion. Provider names remain unchanged at the
owner's request. Approved tooling advisory expiry/removal obligations remain as
recorded in security-review.md; this closeout changes documentation only.
