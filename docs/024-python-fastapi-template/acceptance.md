# SPEC-024 implementation acceptance

- **Status:** Delivered — initial standalone API slice merged and accepted; AC-001–010 passed
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-024](spec.md) · **Design:** [TDD-024](technical-design.md) · **Tasks:** [TASKS-024](tasks.md)
- **Implementation review:** [PR #56](https://github.com/danielbardsley/gptclaw/pull/56)
- **Final reviewed head:** `2da351f2a60f2fd5d659229435e803d0c28cdec8` (repository-selection code `cce026c`)
- **Implementation merge:** `f8b83e851f44e1743e6dd29252c2f1c95c53ae97`, October 11, 2026

The project owner approved the scope and authorized implementation October 11
with “ok, go ahead and implement the spec.” No public exposure, infrastructure/
host package installation or live application GitHub repository creation occurred.
The runtime trial uses the existing reviewed private lifecycle and owned ingress.
The project owner confirmed independent docs/echo behavior on October 11, then
accepted the implementation with “Nice.. Looks good, merge the PR.” PR #56 merged
after final-head CI passed, completing the initial standalone API slice.

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed | Exact catalogue/API generation, no-execution observation, unsafe/occupied-path/provenance refusal and published Next.js identity checked locally and in CI. API provenance is required; frozen Node legacy mapping remains supported. |
| AC-002 | passed | Actual Python 3.13.16/uv 0.13.0 cold acquisition/warm reuse in generated Podman and Docker CI. Receipt/profile/recipe/image identity, version/platform failures and active switching tested. |
| AC-003 | passed | Locked source-preserving restoration and real uv add/update/remove succeed. Offline denied sources/hooks/config/auth/downloads, conflict/abort, failed installation and same-operation interrupted-publication recovery pass. |
| AC-004 | passed | Typed versioned echo, pagination bounds/statuses, invalid input/settings, liveness/readiness and OpenAPI tested in the real generated container and against private HTTPS. |
| AC-005 | passed | Actual EC2 lifecycle/status/bounded logs/tests/reload/syntax recovery/restart/stop/busy behavior passed for the task-owned API, with source retention and owned loopback/resource bounds. Interrupted publication and failure-state scenarios are covered by the isolated suite; no live process was killed to manufacture an interruption. |
| AC-006 | passed | Actual HTTPS docs/assets/schema/API/query forwarding passed from EC2. Mounted nonce/self-hosted docs and hostile-header relative redirects passed in container tests. Stopped URL returned 404; syntax outage produced no successful readiness and recovered. The project owner confirmed from the independent tailnet browser: “Docs load and echo works,” including the requested updated response. |
| AC-007 | passed | Exact-container Black/isort/Ruff/strict mypy/pytest/coverage/Bandit/pip-audit/build/verify pass. Real seeded format/docstring/type/API/import/static-security/coverage defects are rejected. Synthetic advisory findings/unavailability fail; explicit hook preservation/idempotency and real pinned pre-commit config validation pass. The first config-validation attempt used a read-only default cache; a task-owned writable cache corrected that environment setup. |
| AC-008 | passed | Existing Node/Next.js/provider/dependency/toolchain/repository/credential regressions pass. Synthetic real-Git repository creation carries the exact FastAPI release without credential-policy changes. The independent web fixture stayed healthy during API failure/restart/stop; ports/ownership remain independent. |
| AC-009 | passed | Sanitized local/CI/live/client evidence, pins, timings, recovery/refusal trials and fixture disposition are recorded below. All three workflows passed at final head `2da351f`; the project owner accepted the result and authorized PR #56 merge. Implementation merged at `f8b83e8`; only the initial standalone slice is Delivered. |
| AC-010 | passed | Owner-derived guide/config/AGENTS, injected service/src design, complete types/docstrings, safe logs/versioned pagination/readiness/admission/CORS/headers and standards fault cases are implemented. uv/dotenv/Safety adaptations remain explicit; tool-usage material is absent from the normative guide. |

## Local and generated verification

Exact OCI pins are in config/toolchains/v2.json; all package/artifact pins are in
released pyproject.toml/uv.lock. Swagger UI 5.33.1 came from its exact SHA-512-verified
npm tarball; assets, notices, source provenance and file hashes are bundled. Image
execution verified Python 3.13.16 and uv 0.13.0, with no source/credentials mounted
for tool verification. Host app frameworks were not installed.

Executed:

- Prepared `./scripts/check-repository.sh`: 411 tests passed across the combined
  offline suites plus catalogue integrity/immutability. Later focused source
  changes passed Python 25, repository generation 42 and credential 47 tests.
- `.venv-manifest/bin/python scripts/tests/check_python_template.py /tmp/spec024-python-golden-4 --engine podman`: uncached owned profile acquisition/reuse, actual versions, locked preparation/build/full quality, real seeded defect failures, coherent typed uv add/update/remove and frozen restoration passed. CI repeats this with its Docker adapter and final positive gates.
- Changed Bash syntax, Python compilation, relative links and staged/unstaged
  whitespace checks passed; published-release immutability passed against origin/main.
- Generated app checks: 19 pytest tests; actual live critical coverage is 174/176
  statements (98.86%) and 10/10 branches (100%). Both independent 80% gates pass.
  Strict mypy, import/format checks, Ruff, Bandit, locked-graph pip-audit and app
  construction/OpenAPI preflight pass. Public advisory failure is never a clean scan.

Corrected failures are preserved here: CORS preflight initially consumed admission;
a middleware response annotation and factory-boy dynamic typing boundary needed
correction; an authoring cache was accidentally considered for inventory and was
excluded/moved outside release assets. Pinned uv add wrote a project index entry,
which the policy refused before publication; verified `--raw --no-sync` avoids
that entry. The golden fixture's incidental TOML byte-equality assertion was
replaced with dependency semantics plus frozen-source preservation. A new job test
mock bypassed the real runner and was corrected. A final review found legacy hardcoded
repository selection; exact plan/render/broker propagation now has real-Git
synthetic coverage. These failures are not claimed as passed acceptance before correction.

## GitHub CI

Code revision `4498077` passed all configured PR workflows:

- [Private application workflow #58](https://github.com/danielbardsley/gptclaw/actions/runs/38162375279): existing web/toolchain paths plus new real Python Docker/golden job.
- [Development-host workflow #168](https://github.com/danielbardsley/gptclaw/actions/runs/38162375323): repository quality and its configured Terraform mock/validation gates.
- [Tailscale federation workflow #72](https://github.com/danielbardsley/gptclaw/actions/runs/38162375280): its configured validation gates.

Earlier `c07a0fd` passed the same three workflows. Repository-selection code `cce026c` also passed all three workflows:
[private application #59](https://github.com/danielbardsley/gptclaw/actions/runs/38163477625),
[development host #169](https://github.com/danielbardsley/gptclaw/actions/runs/38163477540),
and [federation #73](https://github.com/danielbardsley/gptclaw/actions/runs/38163477650).
Documentation/path-filter head `778b3db` passed
[private application #60](https://github.com/danielbardsley/gptclaw/actions/runs/38163933646),
[development host #170](https://github.com/danielbardsley/gptclaw/actions/runs/38163933638),
and [federation #74](https://github.com/danielbardsley/gptclaw/actions/runs/38163933654).
Final reviewed head `2da351f` passed all three workflows, rechecked before merge:
[private application #63](https://github.com/danielbardsley/gptclaw/actions/runs/38164715128),
[development host #173](https://github.com/danielbardsley/gptclaw/actions/runs/38164715122),
and [federation #77](https://github.com/danielbardsley/gptclaw/actions/runs/38164715108).
GitHub reported the PR mergeable with clean status and no submitted reviews or
inline review threads. The project owner's explicit chat acceptance and merge
instruction are recorded separately from GitHub review submissions.
No local Terraform checks were required because
no Terraform/bootstrap changed, and no protected apply/promotion workflow was invoked.

## Actual EC2 behavior

A task-owned synthetic API and independent Next.js fixture were created through
the reviewed lifecycle. Both bind only loopback, with the approved per-project
resource limits. Actual private HTTPS readiness/liveness/docs/schema/assets/
versioned pagination/echo checks passed; current address, target paths, port
assignments and host identity are intentionally omitted from repository evidence.
They are available in the project owner's private chat/runtime receipts.

The first API start completed in 17.675 seconds; warm start after stop took
6.342 seconds. The independent web fixture started in 54.988 seconds. Base image
blobs were cached: these timings measure new profile/project preparation, not a
clean host or cache-prune trial. Interactive docs use local bundled assets and
require no external CDN or validator service.

A task-owned source change changed echo to `updated: synthetic` within 2.767 seconds.
Injected syntax failure produced no successful readiness (the bounded client timed
out while the gateway's health probe ran), while the web health stayed 200. Fixing
source recovered the updated response. Do not label that timeout an observed 503.
Updated managed API tests passed (10.524 seconds; initial tests 11.691 seconds).
Actual restart (6.49 seconds) recorded stop/start transitions and a fresh operation
ID. Stop (1.036 seconds) revoked the mapping and preserved source; private readiness
returned 404, with independent web health 200. Actual lock contention returned busy
without changing the healthy service. Bounded eight-line logs contained allowlisted
JSON request metadata; no environment/payload/credential dump was collected.

A stopped-target rollback trial using provider 1.5.2 refused API schema 2 with
`invalid` before execution; selected source/manifest/lock hashes stayed identical.
This proves safe unsupported-version refusal, not successful Python execution on
an older provider. A warm start restored the updated API. The installed immutable snapshot records the actual existing persistent
validator interpreter, independent of the temporary implementation worktree's
Python environment; its host path is not exported here.

## Owner acceptance and fixture disposition

The API and web fixture remain running with synthetic data/source. On October 11
the project owner answered “Docs load and echo works” to the explicit independent
client check, which requested echo with `{"message":"synthetic"}` and the updated
`{"message":"updated: synthetic"}` response. This is attributed client evidence,
separate from local HTTPS/CI or ambient browser state.

Client confirmation is complete. Stop only the selected fixtures through the
lifecycle if no longer needed; retain source by default. Golden/authoring directories under
/tmp are task-owned disposable verification data; no unknown project, shared image,
volume or credential material is removed. Existing snapshots/private access and
host/reboot/replacement acceptance remain unchanged and separately tracked.
Review/merge and owner acceptance are complete. Catalogue status is Delivered
for the initial standalone API slice; AI integrations, databases and RUN-006
remain separate scope. The merge did not perform an infrastructure apply or
create a separate application repository.


## Evidence disclosure correction

Automatic approval review rejected a PR-description update that included a private
runtime URL and host metadata. The current evidence/PR summary omit that operational
identity. Earlier branch commits retain the previous evidence version; this follow-up
redacts the current review diff and does not claim a Git-history rewrite. No access
credential, key, authentication file, environment dump or application dataset was
included in that evidence. Private addresses remain available only in this chat's
requested client check and local runtime receipts going forward.
