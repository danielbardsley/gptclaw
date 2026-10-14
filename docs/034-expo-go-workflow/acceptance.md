# SPEC-034 acceptance tracking

- **Status:** Pending — read-only eligibility implemented; Go launch/device proof outstanding
- **Owner:** Project owner
- **Observed:** October 14, 2026 UTC
- **Specification:** [SPEC-034](spec.md) · **Design:** [TDD-034](technical-design.md) · **Tasks:** [TASKS-034](tasks.md)
- **Implementation:** [draft PR #78](https://github.com/danielbardsley/gptclaw/pull/78),
  changes following 9308e0b; not merged or installed as the stable provider.

## Criterion mapping

| Criterion | State | Evidence and remaining work |
|---|---|---|
| AC-001 | Pending | Exact candidate SDK/lock/source-policy and public config/toolchain binding; client/OS drift and unknowns fail certification. Actual supported device matrix and finite certification still pending. |
| AC-002 | Pending | Paired private host protocol and old-generation entry denial exist in SPEC-033. Exact Go launch/nonce handling, URI and local QR/decode remain pending. |
| AC-003 | Pending | Read-only CLI eligibility inspection separates source/client/Metro states with no hidden start/route. Launch/dashboard actions pending. |
| AC-004 | Pending | No physical native interaction, Fast Refresh or full reload accepted yet. |
| AC-005 | Pending | Host stop/expiry/renewal evidence exists separately; physical network/background/compile/reload matrix pending. |
| AC-006 | Pending | Fourteen focused eligibility/CLI drift, privacy and no-mutation cases pass; source/frozen inspection parity on both actual fixtures passes. QR/browser/legacy and complete consumer checks pending. |
| AC-007 | Pending | Immutable candidate packaged; stable installed pointer unchanged. Consumer CI, rollout/rollback, merge and owner supported-matrix acceptance pending. |

## Verification

`python -B scripts/tests/test_expo_go.py` in the prepared Python 3.12 environment
passes fourteen focused cases. The candidate policy reports every platform as
uncertified; no verification date is fabricated. The seven-day maximum certification
age is recorded for future physical evidence, not exercised as accepted certification.

Direct source inspection and the immutable provider's `go inspect` agree for both
actual approved canonical roots with Expo Go 57.0.9 / Android 11 supplied as caller
metadata. Both sources are eligible, both Metro sessions are Ready, and both clients
remain check-required with launch unavailable. CLI duration is 0.767 / 1.173 seconds.
The exact frozen candidate is
`269d34ea87b35eea8cadd75deaa882c585148fd682f9d9ee82d5f0b59e7afb41`.
Timing metadata is excluded from semantic equality; the first harness incorrectly
included that existing CLI field and was corrected. No stable pointer selection,
source change, SDK upgrade, account setup or Tailscale mutation occurred.

Official [Expo Go download metadata](https://expo.dev/go) and
[linking documentation](https://docs.expo.dev/linking/into-your-app/) were rechecked
October 14: SDK 57 is offered, and `exps` denotes HTTPS. This does not verify Go
57.0.9's private nonce/signature/reload behavior and does not authorize advertising
an unproven launch payload. No local QR dependency has been selected yet.

The owner confirms all devices on the development tailnet are permitted. The current
wildcard grant is accepted unchanged. Off-tailnet denial is owner-reported; physical
client membership/access still requires the real device checks.

## Remaining work

Prove exact Go-client launch rules and stale-session binding; implement/verify local
QR and minimum dashboard launch UX; acquire exact iOS physical evidence when a device
is available; complete Android interaction and both-platform recovery checks. Then
verify installed provider/consumer parity and rollback, CI, reviewed merge and owner
acceptance. Retain synthetic counter/navigation/assets for this deliberately scoped
starter/client test; this is not a product or backend CRUD acceptance claim.
