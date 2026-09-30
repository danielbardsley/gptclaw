# TDD-006: Specification Skill

- **Status:** Implemented; review and supported-client acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-006](./spec.md)
- **Tasks:** [TASKS-006](./tasks.md)
- **Last updated:** 2026-09-30

## 1. Approach

Use one repository skill containing instructions and document outlines. The
agent writes and reviews ordinary Markdown through available file tools. No
generator, installer, database, daemon, or external API is required.

Repository skill placement follows the platform architecture. Official
[Build skills documentation](https://learn.chatgpt.com/docs/build-skills)
was consulted on 2026-09-30; actual discovery in the supported connection must
still be demonstrated during acceptance. No global settings are changed to
make a discovery check pass.

## 2. Implemented files

| Path | Responsibility |
|---|---|
| `.agents/skills/gptclaw-specification/SKILL.md` | Name/description frontmatter, applicability, context discovery, new/update/evidence workflow, and links to outlines |
| `.agents/skills/gptclaw-specification/assets/spec.md` | Outcome, scope, requirements, acceptance, decisions, and ownership outline |
| `.agents/skills/gptclaw-specification/assets/technical-design.md` | Implementation choices, requirement mapping, validation, and applicable operational considerations |
| `.agents/skills/gptclaw-specification/assets/tasks.md` | Dependency-ordered tasks, authorization gates, progress, and traceability |
| `.agents/skills/gptclaw-specification/assets/acceptance.md` | Criterion/evidence mapping, actual outcomes, limitations, and remaining work |
| `scripts/tests/test_specification_skill.py` | Narrow package checks using Python's standard library |
| `scripts/tests/fixtures/specification-skill/` | Inert synthetic scenario inputs and reviewer criteria |
| `scripts/check-repository.sh` | Include the focused package checks |
| `.github/workflows/terraform-dev-host.yml` | Include skill paths in existing quality filters if needed; preserve deployment gates |
| `docs/006-specification-skill/acceptance.md` | Implementation and behavioral evidence, created during verification |

These paths are implemented in PR #16. Optional UI metadata is unnecessary
for this slice. The repository
skill remains portable as a directory, but automatic distribution is excluded.

## 3. Workflow and document contract

The entrypoint selects the requested operation and reads only relevant
outlines. For new work, inspect the directory/index to allocate a number; do
not overwrite a collision. Draft specification first, derive the design and
tasks from it, then review cross-document consistency and links. A design may
be prepared alongside a draft spec, but remains a proposal until reviewed.

For updates, read the existing initiative and change only the affected scope.
Retain requirement IDs and evidence; document superseded requirements rather
than reusing their IDs. Reconcile tasks and criteria affected by the change.
Never infer approval from the status text of a copied example.

For acceptance, take actual check outcomes and revision/PR metadata as inputs.
Record missing evidence explicitly. An acceptance document may track pending
work before final acceptance; its existence must never imply completion.

Outlines are flexible authoring aids, not mandatory paragraphs or literal
heading validators. Use stable requirement and acceptance IDs to connect
specification, design, tasks, and results. Mark substantive assumptions and
owner decisions clearly. Relevant risk and recovery detail scales with the
feature; a documentation-only feature needs no invented deployment plan.

## 4. Verification design

Structural tests validate the shipped entrypoint metadata, linked assets, and
required package completeness. Negative fixtures exercise missing metadata
and broken/missing resources. The checks read explicit package paths only;
they do not execute document commands or recursively inspect user projects.
Do not claim semantic safety from heading or string matching.

Behavioral evaluation uses task-owned synthetic repositories with short
source files, guidance, index, catalogue, and existing plans where needed:

| Scenario | Observable result |
|---|---|
| New feature with an occupied initiative number | Selects an unused number, preserves existing files, creates coherent plans and index links |
| Existing approved plan plus a narrow correction | Retains IDs, approval, completed tasks, and unrelated edits without creating another initiative |
| Material scope extension with one unresolved decision | Identifies the decision and proposed scope; continues independent drafting without claiming approval |
| Supplied implementation authorization | Records existing authorization without requesting it again; performs only the operation the scenario requests |
| Passing local check, failed check, and merged PR with pending remote acceptance | Records mixed evidence accurately and keeps delivery pending |
| Unrelated small documentation request | Completes the narrow task without invoking the planning workflow |

Evaluate artifact meaning, diffs, and observed actions, not exact prose. No
real deployment, credentials, external messages, or implementation commands are
needed. Keep reviewer expectations separate from scenario prompts. Execution
must use available, authorized evaluation capabilities; otherwise record the
behavioral scenarios as pending for Daniel. Do not create user-owned chats
without an explicit request. Supported-client selection tests must use fresh
contexts without supplying the expected answer; explicit file loading is not
proof of automatic discovery.

## 5. Maintenance and rollback

Daniel owns changes through reviewed PRs. Preserve historical planning formats;
new outline versions do not rewrite accepted initiatives. A targeted Git revert
of the skill revision restores the prior package while retaining unrelated
changes. Verify the restored package in a fresh context; ongoing chats may
retain previously loaded instructions. No installed global copy needs removal.

## 6. Traceability

| Requirements | Design mechanism | Acceptance |
|---|---|---|
| SPS-001 | Narrow description, context inspection, client selection scenarios | AC-002, AC-006 |
| SPS-002 | Four outlines, stable IDs, numbering and cross-document review | AC-001, AC-002 |
| SPS-003 | Bounded updates and explicit authorization state | AC-003, AC-004 |
| SPS-004 | Criterion/evidence mapping and honest status transitions | AC-005, AC-007 |
| SPS-005 | Instruction-only package, version control, targeted revert | AC-001, AC-007 |
| SPS-006 | Structural checks plus separate behavioral/client evaluation | AC-001–007 |

## 7. Implementation notes

The entrypoint uses only name/description frontmatter, with automatic selection
left at its default. Package tests intentionally support this two-field,
single-line metadata format and ordinary package-relative inline file links;
they are not a general YAML or Markdown parser. Negative cases cover missing
or duplicate metadata, invalid names, absent/empty/unlinked outlines, broken
references, and symlink escape. A sentinel checks that document commands are
not executed. Behavioral inputs and reviewer criteria are separate Markdown
files in the fixture directory.

Both pull-request and main-push quality filters now include `.agents/skills/**`.
Existing protected plan/apply conditions are unchanged. The bundled authoring
validator is an additional local check, not a repository dependency.
