# TDD-051: Patched successor releases and explicit CI retirement

[Spec](spec.md) · [Tasks](tasks.md). Owner: project owner.

Copy the ten failing current release families to 1.2.0. Upgrade Next.js within
16.4 and Python filelock/virtualenv to patched compatible versions. Refresh only
the vulnerable mobile transitive graph while preserving the exact SDK profile.
Remove obsolete mobile exception entries once their findings are resolved.
Reseal only unpublished successors and append catalogue records; keep historical
records and release files byte-identical. No installed provider changes.

Maintain an explicit retirement ledger keyed by exact release with successor and
reason. Matrix enumeration validates it, retains generation coverage for retired
releases and executes every active quality/static release. Do not automatically
retire an arbitrary release because a newer one exists. Update legacy integration
helpers to exercise reviewed successors and expose redacted bounded failure logs.

CI-001 maps to dependency audit, frozen restore and generated full/negative gates;
CI-002 to ledger validation and matrix regression tests plus baseline immutability;
CI-003 to private application integration jobs and diagnostic regression tests.
Run focused tests and the prepared offline repository checker. Use pinned rootless
containers for language commands; retain release-age policy and no install hooks.
Rollback uses a reviewed revert, preserving existing project data and releases.

## Mobile compatibility and package-age disposition

The current Expo CLI still declares Zod 3.25.76 and node-forge 1.4.0. A compatible
range refresh alone does not remove their high findings. Successors use only the
reviewed exact workspace overrides `node-forge: 1.4.1` and
`zod@3.25.76: 4.6.7`; other override keys/values and non-mobile use fail policy.
The direct Expo SDK/native profile remains unchanged. Zod is a major transitive
change: acceptance requires SDK checks, both exports, tests and native integration
jobs; do not infer compatibility from audit success.

The project owner owns the security-fix release-age exception for exactly
node-forge@1.4.1, published 2026-10-27T04:44:07.718Z. Scope: the new mobile
successors only. Reason: remove the vulnerable signature-verification library
while retaining a frozen exact graph. Its age-window exception expires in effect
at 2026-10-28T04:44:07.718Z, after the normal 1,440-minute age requirement is met.
Removal step: omit this selector in the next unpublished successor after that
window; retain immutable historical bytes and validation compatibility. Other
packages retain the normal age gate. No advisory waiver is introduced or renewed.
