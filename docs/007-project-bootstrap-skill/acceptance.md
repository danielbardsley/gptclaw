# SPEC-007 acceptance evidence

- **Status:** Implemented; review, merge, and supported-client acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-09-30
- **Specification:** [SPEC-007](./spec.md)
- **Design:** [TDD-007](./technical-design.md)
- **Tasks:** [TASKS-007](./tasks.md)
- **Implementation PR:** [PR #18](https://github.com/danielbardsley/gptclaw/pull/18)
- **Tested helper revision:** `7632508c38b49dc90ffa6941f33af9aa4bd70c36`
- **Starter/skill behavioral candidate:** `11195ea1cb7f1627bb30c89d81f144863a1eda3c`

Daniel approved the latest specification and authorized implementation on
2026-09-30. No merge, global installation, real project creation, or deployment
is claimed. All generated projects below are task-owned synthetic fixtures.
The copied skill and starter are unchanged between the behavioral candidate and
final helper revision; later changes add race tests and anchor staging.

## Acceptance mapping

| Criterion | Actual state and evidence | Remaining action/owner |
|---|---|---|
| AC-001 | Local pass: starter review and independent explicit bootstrap created the declared files with resolved six-section project guidance and planning-only claims. | Daniel reviews resulting implementation. |
| AC-002 | Passed locally: 28 focused tests cover creation, empty directories, retries, modified/occupied outputs, source and path validation, publication races and failure preservation. | No destructive live test required. |
| AC-003 | Passed locally: exact source allowlist, hashes, copied skill assets, no copied auth/settings/unknown skills, output links and Git boundary verified. | Supported-client evidence remains AC-005. |
| AC-004 | Passed in task-scoped independent evaluation: first-feature plans produced from the generated project only; parent reviewed outputs, scope, links and preservation. | Fresh supported-client behavior remains AC-005. |
| AC-005 | Pending: explicit-loading evaluations are not fresh supported-client discovery/selection. | Daniel exercises explicit and implicit planning in separate supported-client contexts. |
| AC-006 | Partial: local checks pass, evidence and procedures recorded; CI below. | Review, merge, and record actual merged revision; keep catalogue status honest. |

## Verification

- `python3 -B scripts/tests/test_project_bootstrap.py`: 28 tests passed on final helper.
- `./scripts/check-repository.sh`: repository invariants and all 79 tests passed
  (installer 17, host bootstrap 5, repository guidance 10, nested guidance 9,
  specification skill 10, project bootstrap 28).
- `python3 /home/forge/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/gptclaw-project-bootstrap`: passed.
- `bash -n scripts/check-repository.sh`: passed.
- Python syntax compilation passed during implementation; its task-created
  bytecode was removed. Repository tests import with `-B` to avoid new caches.
- `git diff --check` and `git diff --cached --check`: passed.
- Final CLI smoke used the full helper revision in a temporary parent: preview
  returned ready, creation returned created, unchanged retry returned
  already-created. Provenance contains 10 file hashes for 11 generated files
  including provenance itself. Fixture cleaned after assertions.

No Terraform source changed; local Terraform commands were not run. Existing
PR CI runs its full quality job, including Terraform. New template paths are
included in both pull-request and main-push filters; protected deployment
conditions are unchanged. No dependency installation or infrastructure mutation
was performed.

## Behavioral evaluation

An independent agent explicitly loaded the bootstrap skill and invoked the real
helper for a synthetic Pebble Notes planning repository. Preview, creation, and
repeat check succeeded. It checked 10 provenance hashes, 16 relative links,
Markdown whitespace, Git main, absence of commits/remotes, and no in-progress
marker. All 11 expected files were present and untracked. The fixture was
retained for the separate new-project evaluator, with no application or first
feature created by bootstrap itself.

The second evaluator is permitted to read/write only the generated project,
including its copied skill. Original-checkout access is disallowed by its task
resource boundary. This is not an OS sandbox or proof against a malicious
agent; evidence is the actual observed task and artifacts, not filesystem
isolation. Neither evaluator creates a user-owned chat or accesses the network.
Supported-client automatic selection remains separate.

## Recovery, updates, and limitations

Creation is exclusive per entry, not an atomic whole-project transaction.
Publication errors preserve the destination and in-progress marker with any
partial files; automatic retries refuse that incomplete project. Inspect it
before a separately scoped repair/adoption. No automatic deletion, reset, or
repair command is provided. Ordinary exceptions clean only owned staging;
process/host termination can leave an owned staging directory for operator review.

Linux procfs, POSIX directory descriptors, and same-filesystem hardlinks are
required. Collision defenses do not provide isolation from a hostile process
running as the same user. A source SHA is provenance, not proof of review; the
skill requires selecting an actually reviewed revision. Source inventory changes
require a reviewed helper allowlist update. Files after bootstrap are project-owned.

Updates compare provenance with local adaptations in an explicit project review.
A targeted reviewed revert rolls back the source helper/starter/skill without
deleting or modifying created projects. The active workspace may not permit
writing the suggested sibling-project parent; follow actual session permissions.
No request to create a project is inferred from implementation authorization.

## CI and delivery

[Run #66](https://github.com/danielbardsley/gptclaw/actions/runs/36788883197)
passed for `896b35d`, before the final parent-directory staging fix. Final-helper
CI passed as recorded below. AGT-005 remains Planned pending
review/merge and final acceptance; prior initiatives are not marked complete.


## Completed handoff and final CI

A second independent evaluator, given only the generated project's permitted
workspace and a request to plan notes creation/listing, read its local guidance
and copied specification skill. It created `docs/001-create-and-list-notes/`
with linked spec/design/tasks, and updated only its local index/catalogue.
The design proposed an ordered local JSON file, clearly awaiting review. Stable
requirements and measurable criteria covered title/body preservation, creation
order, persistence, failure handling, and synthetic data. No application code,
commands asserted as installed, inherited platform backlog, or fabricated
approval/test result appeared in the reviewed artifacts.

The parent inspected all three generated plans and catalogue; checked the eight
unchanged starter/skill hashes and all 26 relative file links after planning.
Only the expected index/catalogue files changed from bootstrap, plus the three
new plans. Git remained unborn main with all output untracked. Git whitespace
checks alone do not cover untracked files; content was directly inspected.
The evaluator reported no source-checkout reads, network, credentials, installs,
commits, or remotes. Source separation is the task access boundary described
above, not an OS-enforced access experiment. Both evaluators used explicit skill
loading, so AC-005 is still pending. The parent removed only the owned synthetic
evaluation directory after recording and checking this evidence.

[Run #67](https://github.com/danielbardsley/gptclaw/actions/runs/36789124747)
passed at final helper revision `7632508`. Repository checks, Terraform format,
backend-free initialization, validation, and tests passed. Protected plan/apply
were skipped. The final documentation-only evidence commit is separate from
this implementation-revision CI result. No merge or deployment was performed.

Documentation link review passed 53 relative file links across seven skill/
planning/index/catalogue documents; template output links are additionally
validated by the helper and its isolated tests. External URLs and heading-anchor
semantics are outside the local file-link check.
