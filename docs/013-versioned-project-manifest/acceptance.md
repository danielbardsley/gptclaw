# SPEC-013 acceptance evidence

- **Owner:** Daniel
- **Evidence date:** 2026-09-30 (America/New_York)
- **Status:** Local verification and implementation CI passed; owner review and merge pending
- **Specification:** [SPEC-013](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **Tested implementation revision:** `63698085467028467d8076191d1e3ebf83d63a45`
- **Implementation PR:** [PR #22](https://github.com/danielbardsley/gptclaw/pull/22)
- **Authorization:** Daniel approved the specification and explicitly requested
  implementation in this chat. Implementation acceptance and merge are separate.

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Passed locally | Example, field boundaries, all required fields, nested unknown fields, strict integer/version semantics, ports, paths and commands are covered by the validator suite. |
| AC-002 | Passed locally | Public/Funnel, secret/environment, persistent data, host-port/bind and generated-state fields are rejected; reference distinguishes declarations from runtime isolation and secret detection. |
| AC-003 | Passed locally | Actual unreadable file/directory checks as unprivileged forge; missing/symlink/FIFO/directory inputs, symlink swap during open, malformed/restricted YAML, UTF-8 and size/depth limits pass. Instrumented network/process denial, literal environment arguments, command sentinels and unchanged project bytes pass. |
| AC-004 | Passed locally | Human/JSON and exit statuses, missing dependencies/schema, invalid/nonlocal schema, sanitized internal failures, deterministic bounded error lists and input redaction pass. |
| AC-005 | Passed locally | CLI copy/validate/break/fix example passes without Node/runtime; CLI launched from project directory ignores project modules. All 28 existing planning-bootstrap tests pass unchanged. |
| AC-006 | Pending | Local repository checks and implementation CI pass. Daniel's implementation review and merge remain pending. No running application or deployed behavior is claimed. |

## Executed verification

Environment: Linux, unprivileged `forge`, Python 3.12.3, isolated environment
`/tmp/gptclaw-prj001-venv`, with all seven runtime dependencies pinned and hashed
in `requirements/project-manifest.txt`. Setup used a digest-verified pip wheel;
no host packages, privileged settings or runtime services changed.

- `python3 scripts/setup-project-manifest.py --venv /tmp/gptclaw-prj001-venv`
  succeeded from a host with no pip/ensurepip. The environment is retained for
  review/use; tests clean their own temporary projects.
- `/tmp/gptclaw-prj001-venv/bin/python -B scripts/tests/test_project_manifest.py`
  passed the initial 25 tests. Two additional tests subsequently passed within
  the full repository run: setup preserves an existing destination and CLI
  execution from a project directory does not import project modules.
- After `source /tmp/gptclaw-prj001-venv/bin/activate`,
  `./scripts/check-repository.sh` passed all 134 tests and repository invariants:
  installer 17, host bootstrap 5, repository guidance 10, nested guidance 9,
  specification package 10, project bootstrap 28, workflow packages 9,
  ADR 19, manifest 27. No tests were skipped.
- The first full run failed the root guidance size check (8,386 bytes).
  Shortening the newly added setup guidance to 8,168 bytes corrected it; the
  subsequent complete run passed. No test or size limit was weakened.
- `bash -n scripts/check-repository.sh` and Python AST syntax checks for the
  four new Python files passed. `git diff --check` and `git diff --cached --check` passed;
  all 119 local file targets in the staged Markdown resolved. External URLs
  and heading anchors were not checked.

Network denial evidence uses patched socket creation/connection and subprocess
APIs during validation, not host firewall changes or a deployed network boundary.
Symlink substitution and permissions tests exercise real filesystem operations
only in test-owned directories. Validation's bundled reference resolver cannot
retrieve external schemas. Package downloads occur only during explicit setup.

Local Terraform commands were not run because no Terraform source changed.
[CI run #73](https://github.com/danielbardsley/gptclaw/actions/runs/36812491579)
passed for implementation revision `6369808`, including pinned Python setup,
isolated dependency setup, repository checks, Terraform formatting, backend-free
initialization, validation and tests. Protected plan/apply were not requested;
this is PR CI evidence, not an infrastructure deployment. Updated repository guidance passes structural
checks; fresh-task instruction-loading behavior has not been tested and no
installed host policy was changed.

## Delivery and remaining work

Implementation revision `6369808` is committed and pushed on
`codex/prj-001-manifest-spec` in PR #22.
Daniel owns implementation acceptance and merge. PRJ-001 remains In review,
not Delivered. AGT-006 live runtime acceptance and the working-private-app
milestone remain open. Rollback is a reviewed revert of tooling; preserve
independently authored manifests and any later runtime state.
