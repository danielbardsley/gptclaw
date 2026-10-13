# SPEC-031 dependency advisory disposition

- **Status:** Proposed temporary exceptions; owner decision pending
- **Owner:** Project owner
- **Observed:** 2026-10-13 (America/New_York)
- **Scope:** Exact SDK-57 starter's bounded development/CI source-quality and JavaScript/asset export jobs only
- **Proposed expiry:** End of October 27, 2026 (America/New_York)

The actual frozen starter passed lint, type and native-component interaction checks,
but its high-severity audit gate failed. The official registry/advisory records list
no patched version for these two findings:

| Advisory | Dependency and failure | Proposed bounded treatment |
|---|---|---|
| [GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv) | node-forge 1.4.0; RSA signature verification accepts malformed nested algorithm data. Pulled through Expo CLI/certificate tooling. | Allow this exact advisory/package/version in source-only build tooling. This slice does not sign/verify releases, publish updates, compile native binaries, run a Metro service or pass signing credentials. |
| [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) | braces 3.0.3; deeply nested patterns can exhaust the stack. Pulled through Metro/test glob tooling. | Allow this exact advisory/package/version for owned source checks/export jobs with finite CPU, memory, PID, output and time bounds; no exposed service accepts remote patterns. |

These mitigations are an assessment of the selected workflow, not proof the packages
are fixed or safe for all uses. No blanket severity suppression is proposed. The
remaining moderate findings stay visible; unexpected high/critical findings,
version changes, unknown audit format/network failure or expiry fail the gate.
Exceptions apply to no web/API policy, product release, Metro service or production
pipeline. Job inputs remain approved source and public locked packages; no home,
engine socket, database data or credential store is mounted.

If approved, record the owner disposition and exact advisory/package/version/expiry
in a checked policy consumed by both CLI and generated CI. Add tests for unrelated
findings, mismatched versions and expiry. Generated projects retain this record and
must obtain fresh review or adopt a patched reviewed starter before expiry.

Removal: the project owner owns follow-through; the implementation author checks
upstream fixes, pins verified patched packages in a new immutable starter release,
reruns all gates and removes the exceptions. If no patch is accepted by expiry,
source verification becomes blocked; do not extend silently or mutate an already
published starter release. No exception has yet been enabled.

The approved specification requires disposition for a “change outside the approved
scope.” This proposal changes the failed security gate's treatment and therefore
requires an explicit owner decision before claiming security acceptance.
