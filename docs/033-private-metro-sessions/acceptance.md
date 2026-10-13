# SPEC-033 acceptance tracking

- **Status:** Pending — implementation in progress; no Metro/device acceptance
- **Owner:** Project owner
- **Observed:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md) · **Tasks:** [TASKS-033](tasks.md)
- **Context:** Main fd6566426e0f18f16bc19150edcc113902da3e84;
  planning commit 66c19a26eb9fba81812165b6c7bda3d390e776ed / [PR #77](https://github.com/danielbardsley/gptclaw/pull/77).
  Local runtime preparation is on codex/mobile-metro /
  [draft PR #78](https://github.com/danielbardsley/gptclaw/pull/78); merge/CI/runtime are pending.

## Criterion mapping

| Criterion | State | Current evidence and remaining action |
|---|---|---|
| AC-001 | Pending | Schema-6 opt-in/strict input validation, canonical guarded metadata migration and older-provider rejection have local evidence; session capability/descriptor and installed rollout remain pending. |
| AC-002 | Pending | Offline ownership/deadline/fixture guards pass; real two-session lifecycle/disconnect/expiry still required. |
| AC-003 | Pending | No Metro SDK or physical transport test run. Streaming/private protocol and separate native iOS/Android proof remain required. |
| AC-004 | Pending | No Serve changes performed; exact operator plan/readback and permitted/denied private access still required. |
| AC-005 | Pending | Spike plan says approval-pending and unavailable start is blocked; production typed observation/descriptor/collector remain to implement. |
| AC-006 | Pending | Fresh audit, disabled exact runtime admission and offline safety tests recorded in [security proposal](security-review.md); owner disposition and real runtime revocation/secret checks remain. |
| AC-007 | Pending | Offline absent/foreign ownership cleanup passes; actual crashes, leases, compatible provider refresh/rollback and app regression evidence remain. |
| AC-008 | Pending | Local source/admission/protocol evidence and all four CI workflows passed at fb7f4b2. Final source-job guard CI, actual Metro/installed operations, operator/device acceptance and merge remain required. |

## Actual local verification

- Eight cases in `python3 -B scripts/tests/test_metro_security.py` passed.
- Twenty-one cases in `python -B scripts/tests/test_metro_spike.py` passed using the
  prepared Python 3.12 manifest environment. Synthetic offline fixtures only.
- `metro_spike.py --project-root /srv/forge/projects/mob001-accept-one --origin
  https://forge-dev-01-4.tail8c3304.ts.net:8443 --seconds 300` returned approval-pending,
  a read-only plan with ten filtered source files, and no route operation.
- The same command with `--apply` returned exit 1 / blocked at the absent owner
  runtime approval, before lock/store/container/network writes.
- `./scripts/check-repository.sh` completed with exit 0 using the prepared manifest
  environment. This checkpoint ran the full offline repository suite; subsequent
  protocol integration was verified with the focused tests below.
- Ten cases in `python -B scripts/tests/test_metro_protocol.py` passed against
  task-owned loopback HTTP fixtures: a 3 MiB stream, byte/header/deadline limits,
  redirects, foreign/credential URLs and malformed/truncated manifests. An initial
  deadline-test revision exposed an EOF/socket-close bug; the corrected revision
  passed all ten cases. These are synthetic protocol tests, not an SDK/phone result.
- Diff whitespace, checker shell syntax and new relative-link review passed.
  All 59 focused security/spike/protocol/opt-in cases are registered in the checker.
  This includes a real host-identity denial case and explicit opt-in recovery tests.
  The full local gate completed with exit 1 from the two obsolete manifest-test
  assumptions described below. Every other suite passed. The corrected complete
  28-case manifest suite passed separately, and CI then passed at fb7f4b2.

No actual Metro/container startup, private route, phone client, or rollout was
executed. Source-check audit containers are covered by the existing source-only
scope and do not prove runtime acceptance. Terraform/deployment checks are not
applicable to this source preparation.

## Owner reports and remaining work

An authorized owner relay reports Android 11 on the development tailnet, with
Expo Go described as up to date. Exact model, OS build and client version remain
unknown; no actual native load/interaction/reload was reported for this initiative.
No iPhone is confirmed. Both platform criteria remain pending.

Use only proposed retained mob001-accept-one/two synthetic roots after exact scope
approval, preserving their Git history/source. Shelfmark, Trailboard, existing app
routes/data and immutable starter releases have not been changed. Security approval,
SDK spike, provider/transport, exact operator scope, physical evidence and merge
remain distinct gates; the active goal stays open.

## Source-contract progress

The source provider now reports development version 1.12.0, source manifest schemas
1–6, `metro_actions: [enable]`, an empty Metro session-schema list, and runtime
manifest schemas 1–4. Schema 6 is not advertised as a working runtime. Existing
schema-5 generation and immutable releases are preserved. Frozen provider bundling
includes the new validator/migration; no new snapshot was selected for live operation.

The final opt-in fixture suite passed 18 cases, including exact toolchain/profile
fingerprints and wrong-toolchain denial. Initial failures were fixture assertions that overlooked
creation's existing identity lock; assertions now compare against the actual initial
store. The full regression run found two outdated manifest-test assumptions: schema 6
was still listed as unsupported, and a proposed sixth cache slot exceeded the
existing five-entry test bound. Unknown-version coverage now uses schema 7; the
five-entry cache bound was preserved. Both focused cases passed after correction.
The completed full run had no other failures. Its exit 1 is retained rather than
reported as a clean rerun. The complete corrected 28-case manifest suite passed
and the new-head CI quality jobs later passed.
A canonical read-only plan for retained mob001-accept-one succeeded with no apply,
service or route change. Current stable launcher remains provider snapshot
48a1131521aae5c2e6671faec8b3a1701c56976de6a3099f1d1d0887a4f5a5ba / version 1.10.1.

That actual installed provider rejected a task-owned schema-6 fixture via `validate`
with exit 1 and `version`; the fixture was unchanged and no runtime was started.
Only the owned temporary fixture was removed. This is installed backward rejection
evidence, not installation or session/rollback acceptance for 1.12.0.

At 319925ab20653fc6ee14d9ca2f579c7ad493adf2, the private application workflow
[passed](https://github.com/danielbardsley/gptclaw/actions/runs/38480679547). The dev-host
and Tailscale-federation workflows failed in repository checks because the new
simulation tests incorrectly hit forge's UID-1002 guard on the runner. The test
boundary now mocks operator admission only for simulated jobs; a separate negative
case proves the actual foreign/root UID guard remains enforced. There was no apply,
permission change or genuine Metro job. Final CI at the new revision remains pending.

## CI and final source-job guard checkpoint

At fb7f4b20185905a0f5b355a4640c584aff8396f1 all four workflows passed:
[private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38484536211),
[dev-host checks](https://github.com/danielbardsley/gptclaw/actions/runs/38484536150),
[Tailscale-federation checks](https://github.com/danielbardsley/gptclaw/actions/runs/38484536222),
and [dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38484536162).
Protected infrastructure plan/apply were skipped, not executed. Source creation,
legacy apps/database/dashboard and invariant/format/validate/test/scan results
remain separate from Metro/native acceptance.

A final review added source-job admission before opt-in publication: checking or
unknown source jobs block before container commands; any extant job container
blocks even when its saved phase is idle. Only an explicitly absent job permits
publication. The two added cases and the existing normal-upgrade case passed
(three focused cases). No real job/container was stopped or started; stale state
and both metadata copies were preserved. The 18 prior opt-in cases plus these two
new cases, 21 preflight cases, eight admission cases and ten protocol cases cover
59 focused scenarios. Final CI for this small additional guard remains pending.
