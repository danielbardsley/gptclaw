# ACCEPTANCE-031: Expo / React Native creation foundation

- **Status:** Implementation in review; local verification in progress, installed/repository/owner acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Spec:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md) · **Tasks:** [TASKS-031](tasks.md)
- **PR:** [#73](https://github.com/danielbardsley/gptclaw/pull/73)
- **Implementation baseline:** 6c8ce2b; subsequent documentation c2b3dbb and additional transaction tests are being verified
- **Exact starter:** expo-react-native@1.0.0; digest 662482948e2c3b5f5ab8160cc2c23ba6ab1ba269831583e7155ac477cb2cabfa

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed local; CI pending | Exact list/show, digest/path/release checks; historical release immutability against origin/main passed. Default remains Next.js. |
| AC-002 | passed local | Two-source generation/identity tests, valid schema 5 and typed static configuration, occupied/duplicate identity and dynamic/native rejection. |
| AC-003 | passed local | Generation performs no repository execution/network download; normalized source equivalence, destination/symlink/failure preservation and existing catalogue race/recovery regressions passed. |
| AC-004 | pending final/live | Real frozen install and exact image verification passed; scoped SDK/policy denials passed. The 22-case mobile suite passed, including add/remove/source retention and exact-operation install recovery; installed proof remains. |
| AC-005 | pending final | Authored starter passed lint/types/interaction/coverage, exact advisory policy and both native exports. Both generated apps completed frozen install and all seven source checks/exports. Counter-behavior and type defects were rejected; an initial debugger lint fixture was permitted by the upstream lint config, so a real syntax defect and style defect were rerun and rejected. The complete corrected driver is also a CI gate. No device or signed-binary acceptance is claimed. |
| AC-006 | pending | Local private Git/repository-plan regression passed, including mobile identity/profile fingerprints. Exact two private live targets and supporting credential policy require the owner disposition in acceptance-targets.md. |
| AC-007 | pending CI | Generated guidance, locked source workflow and quality helper implemented; native golden/defect CI and generated-private-repository final-head CI remain. |
| AC-008 | pending live | Dashboard frozen install, unit/type/build, real socket/HTTP and pinned browser regression passed, including mobile source/unavailable runtime. Actual updated collector/frontend and new private repo rows not yet deployed. |
| AC-009 | pending | Source/installed packaging tests passed locally; complete final gate/head CI, owned private refresh/rollback and owner creation/edit/check acceptance remain. No merge or Delivered claim. |

## Executed evidence and corrective checks

Use the prepared isolated Python 3.12 environment for offline repository tests;
Node/package commands run in the existing exact rootless Node 24.21.0/pnpm 12.10.1
image, with finite CPU/memory/PID/time bounds and no host language package installs.

- Official Expo 57.0.28 package and starter metadata were integrity-verified without
  running a generator. Frozen installation passed in 21 seconds with scripts disabled.
- The authored starter's formatter/lint/type/interaction tests, 100% counter coverage,
  exact SDK check, approved advisory policy and iOS/Android exports passed. SDK 57
  selects React Native 0.86.3/React 19.2.3; Native app compilation was not run.
- Initial ESLint 10 was incompatible with its React plugin; exact ESLint 9.39.5 passed.
  Missing Jest ambient types were corrected. Controlled press timers and a finite
  15-second test deadline preserve interaction assertions under bounded scheduling.
- Focused mobile generation suite: 18 cases passed; catalogue suite: 21 passed;
  repository suite: 43 passed. Additional immutable-policy/state/transaction cases
  are tracked in the final gate rather than inferred from those earlier counts.
- Initial release inventory accidentally included Jest cache; caches were excluded
  and the frozen inventory now contains 31 source files. SDK/test lock references
  require five exact public aliases, accepted only by the mobile profile.
- Dashboard check: frozen install, seven frontend tests, type generation/check,
  production build, actual Unix socket/HTTP and pinned browser checks passed. The
  first attempt could not find a retired cached browser image; a fresh verified
  pinned image completed all checks including native source/unavailable-runtime UI.
- A broad gate started during release authoring and failed on changing hashes; that
  run is retained separately. A subsequent gate's only recorded failure was the
  legacy cache-bound assertion of four rather than five supported schemas. The
  corrected 28-case manifest suite passed; final full-gate outcome is pending.
- Initial combined generated-app verification exceeded its 300-second deadline
  under concurrent checks. Final CLI/golden orchestration runs serial bounded steps;
  no individual job resource/deadline ceiling was increased. The timed-out task-owned
  container subsequently completed/was removed; no existing service was stopped.

Two approved unpatched tooling advisories remain explicit, with expiry at the end
of October 27, America/New_York. Moderate findings remain visible; this is not a
clean-vulnerability assertion. See [security review](security-review.md) for owner
approval, exact versions, mitigations and removal/follow-through.

## Private scope, safety and remaining work

No native acceptance repository, Metro session, application service, EAS account,
native binary or infrastructure mutation has been created by this implementation.
Existing Shelfmark/Trailboard source/data/containers remain outside fixture operations.
Synthetic counter/about content and the local starter icon are deliberately retained
for this starter's stated acceptance purpose; product adaptation must review/remove
unwanted demos and test the product's actual behavior.

The exact four-name credential/fixture proposal is in
[acceptance-targets.md](acceptance-targets.md). Automatic approval review rejected the
broader unapproved 64-name schema/helper command; none of that command ran. The
smaller proposal awaits explicit authorization. Archived bindings are not deleted
or silently adopted. Source-only work continues independently.

Complete final local/CI checks, authorized owned private provider/dashboard rollout,
source/installed parity and rollback, live private repository CI and owner acceptance.
Retain synthetic fixtures/logs for review, with source archival only under the stated
retention plan; no automatic remote-repository or application-data deletion. Mark
only MOB-001 Delivered after merged implementation and all criteria pass. TPL-004's
full device acceptance and mobile M1–M4 remain separate.

CI on c2b3dbb: dashboard passed; web/API/group/database jobs passed where reached.
The new native job had duplicate isolated-environment setup, and native CLI-denial
unit tests assumed forge UID on the differently numbered GitHub runner. Corrected
the setup and exercised the non-HTTP dispatcher directly in isolated tests, keeping
the real forge-only CLI gate unchanged. Final head CI must be rerun; no failed run
is reported as successful.
