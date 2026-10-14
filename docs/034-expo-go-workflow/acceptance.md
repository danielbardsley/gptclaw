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


## Local QR and current iOS prerequisite checkpoint

The exact reviewed encoder/test decoder are pinned and described in
[QR review](qr-review.md). Thirteen frontend tests, type checking, production build
and the complete portable socket/HTTP/browser gate passed. The final SVG independently
decodes after actual browser rasterization; fresh complete frontend audit has zero
findings. No Go product link or native-device certification follows from these checks.

The official [September 3 Expo login notice](https://expo.dev/changelog/expo-go-57-login)
rechecked October 14 says latest iOS Go requires matching CLI/app account login, with
Android enforcement described as future. The candidate iOS profile now explicitly
reports that prerequisite as outside the credential-free scope and routes to MOB-004.
Fifteen focused inspection cases pass, including acquisition/login-bypass rejection.
The owner requested continued iOS software development; the native protocol/software
path remains, with physical/client acquisition and any separate credential/build scope
pending. No account credential or login was installed.

An Android candidate launch-rule check was requested using current session-bound
private URLs; no device answer has arrived. The second session subsequently reached
its original expiry and became unavailable, with exact owned cleanup verified. The
first candidate remains finite. These are implementation prerequisites and pending
owner evidence, not completed physical criteria.


Updated source/frozen inspection parity passed on both actual fixtures for Android
57.0.9 / Android 11 and the assumed iOS client/OS input. Android remains check-required;
iOS returns the explicit out-of-scope CLI-login reason; Metro separately shows the
first Ready and the second expired. Frozen candidate
`2e51878ec8cea1c71a405969cc5c8f9dc423acc25a77cda228cd9f7683ccf3da` matches source;
observations took 0.735–1.107 seconds. Immutable dashboard release
`953e8e25851985e8ad1be08eeb791392fa9e93d85477abd0f84bfefcebf46a78` was prepared
with existing status/link flags; no stable pointer or active dashboard selection had
changed at this checkpoint. Preparation is not installed acceptance.
