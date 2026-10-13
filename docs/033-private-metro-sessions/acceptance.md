# SPEC-033 acceptance tracking

- **Status:** Pending — implementation in progress; no Metro/device acceptance
- **Owner:** Project owner
- **Observed:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md) · **Tasks:** [TASKS-033](tasks.md)
- **Context:** Main fd6566426e0f18f16bc19150edcc113902da3e84;
  planning commit 66c19a26eb9fba81812165b6c7bda3d390e776ed / [PR #77](https://github.com/danielbardsley/gptclaw/pull/77).
  Local runtime preparation is on codex/mobile-metro; merge/CI/runtime are pending.

## Criterion mapping

| Criterion | State | Current evidence and remaining action |
|---|---|---|
| AC-001 | Pending | Existing canonical schema-5 fixture accepts read-only spike planning; opt-in contract/provider tests remain to implement. |
| AC-002 | Pending | Offline ownership/deadline/fixture guards pass; real two-session lifecycle/disconnect/expiry still required. |
| AC-003 | Pending | No Metro SDK or physical transport test run. Streaming/private protocol and separate native iOS/Android proof remain required. |
| AC-004 | Pending | No Serve changes performed; exact operator plan/readback and permitted/denied private access still required. |
| AC-005 | Pending | Spike plan says approval-pending and unavailable start is blocked; production typed observation/descriptor/collector remain to implement. |
| AC-006 | Pending | Fresh audit, disabled exact runtime admission and offline safety tests recorded in [security proposal](security-review.md); owner disposition and real runtime revocation/secret checks remain. |
| AC-007 | Pending | Offline absent/foreign ownership cleanup passes; actual crashes, leases, compatible provider refresh/rollback and app regression evidence remain. |
| AC-008 | Pending | Local preflight evidence only; CI, installed operations, operator/device acceptance and reviewed merge remain required. |

## Actual local verification

- Eight cases in `python3 -B scripts/tests/test_metro_security.py` passed.
- Seventeen cases in `python -B scripts/tests/test_metro_spike.py` passed using the
  prepared Python 3.12 manifest environment. Synthetic offline fixtures only.
- `metro_spike.py --project-root /srv/forge/projects/mob001-accept-one --origin
  https://forge-dev-01-4.tail8c3304.ts.net:8443 --seconds 300` returned approval-pending,
  a read-only plan with ten filtered source files, and no route operation.
- The same command with `--apply` returned exit 1 / blocked at the absent owner
  runtime approval, before lock/store/container/network writes.
- Diff whitespace and checker shell syntax passed. Broader offline repository
  checks are running; no overall pass is claimed yet.

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
