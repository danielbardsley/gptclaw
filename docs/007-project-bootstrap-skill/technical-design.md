# TDD-007: Project Bootstrap Skill

- **Status:** Implemented; review and acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-007](./spec.md)
- **Tasks:** [TASKS-007](./tasks.md)
- **Last updated:** 2026-09-30

## Approach

Pair a short workflow skill with one deterministic Python standard-library
helper for bounded file creation. A helper is justified by destination validation,
provenance, collision checks, and repeatable failure handling. Keep product
intent and clarification in the skill; do not build a general scaffolding CLI.

The implementation introduces a versioned planning starter under
`templates/projects/planning/`. Adapt the existing AGT-002 template once into a
starter with explicit project metadata fields, then fill those fields during
creation. Template approval is through this feature's implementation PR; it is
not permission to execute arbitrary third-party templates.

## Components

| Path | Responsibility | Requirements |
|---|---|---|
| `.agents/skills/gptclaw-project-bootstrap/SKILL.md` | Gather scope, explain output, invoke bounded helper, verify and hand off | PBS-001, PBS-005 |
| `templates/projects/planning/` | Versioned README, root-guidance, Git-ignore, and planning-index/catalogue sources using inert template filenames | PBS-003 |
| `scripts/bootstrap-project.py` | Validate explicit inputs/source/destination, render allowlisted files, copy skill, record provenance, initialize Git | PBS-002–004 |
| `scripts/tests/test_project_bootstrap.py` | Standard-library isolated positive/negative/failure/retry tests | PBS-002–005 |
| `scripts/tests/fixtures/project-bootstrap/` | Inert synthetic metadata and behavioral prompts with separate reviewer criteria | PBS-001, PBS-005 |
| `scripts/check-repository.sh` and existing quality workflow | Run helper tests and cover new template paths; preserve deployment gates | PBS-005 |
| `docs/007-project-bootstrap-skill/acceptance.md` | Actual verification and delivery evidence, added during implementation | PBS-005 |

## Source and output contract

Read allowlisted starter and specification-skill files from an explicit full
commit SHA in the local GptClaw Git object database, never silently from a dirty
working tree. Require a locally available source revision and report its identity;
do not fetch arbitrary sources or infer that any supplied SHA is reviewed.
Initially select the merged implementation revision for normal use. Isolated
pre-merge tests may use an explicitly identified candidate revision without
claiming release approval. Subsequent calls use the explicit reviewed baseline.

Output comprises README.md, AGENTS.md, .gitignore, docs/README.md,
docs/platform/features.md, the complete `.agents/skills/gptclaw-specification/`
package, and `docs/bootstrap-provenance.json`. Provenance records the source
repository URL and full SHA, starter version, and hashes for copied skill files
and generated starter files. It contains no timestamps needed for correctness,
secrets, auth data, machine-specific source paths, or speculative runtime schema.
This file is bootstrap evidence, not PRJ-001's future project manifest.

The specification skill remains named `gptclaw-specification` to identify its
origin. Its current workflow already resolves planning paths against the target
repository; inspect and adjust portability wording only if tests demonstrate a
need. Do not strip approval/evidence safeguards during distribution.

## Safe creation and retry

Validate metadata and resolve the parent/destination; reject path traversal and
symlink ambiguity. Bound writes to the explicit target and task-owned staging
area under its parent. Check both filesystem occupancy and Git ancestry before
creation. Render all output in staging, verify references and hashes, and
initialize Git there using fixed commands, no template hooks or network.

Publish only with a no-clobber operation or equivalent exclusive reservation;
plain replacement rename that could overwrite a concurrent directory is not
sufficient. Implementation must define and test the publication strategy before
shipping. Existing empty destinations must receive equivalent collision
protection; fail safely if their identity or contents change. Keep a journal of
owned outputs if needed for recovery. Cleanup removes only this run's confirmed
staging artifacts, never an unverified project path.

A repeat invocation verifies provenance and expected generated files. If an
unchanged completed project matches the same inputs/revision, report already
created without writes. If modified, incomplete, or conflicting, report the
specific condition and preserve files for review. General repair/adoption and
automatic upgrades are excluded. Do not erase work merely because generation
failed after creating some files.

The default parent may be outside the active workspace permission boundary.
Explain the exact target and request only the required write permission when
needed; never treat repository guidance as a permission grant. Tests use /tmp.

## Verification and rollout

Test creation for a new and an existing empty directory, provenance and copied
asset hashes, local links, fully resolved guidance, and clean separation from
source settings. Test failure before publication, destination changes during
publication, nested repositories, symlinks, invalid slugs, occupied files,
retries, and modified outputs using synthetic fixtures and ownership sentinels.
Do not execute application commands or fetch packages to validate a starter.

Evaluate a real request to create a small planning project in an isolated
fixture, then give an independent evaluator only that project and a request to
plan its first feature. Record source-read restrictions, files/actions, and
outcomes. Supported-client discovery uses separate fresh contexts and remains
pending if unavailable. Retain sanitized evidence before owned-fixture cleanup.

Rollout adds the bootstrap capability to GptClaw; it does not modify existing
projects. A reviewed revert removes/restores the helper and starter revision.
Created projects are independently owned; rollback does not delete them or
replace their skill copies. Updates later compare provenance and local changes
in project-owned reviewable diffs.

## Traceability

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| PBS-001 | Narrow skill, explicit inputs and side effects | 1.1–1.3, 3.1 | AC-001, AC-006 |
| PBS-002 | Bounded helper, exclusive publication, preservation tests | 2.1–2.3 | AC-002, AC-006 |
| PBS-003 | Approved starter, resolved local guidance, output checks | 1.2, 2.2, 3.1 | AC-001, AC-003 |
| PBS-004 | Immutable allowlist, full skill copy, hashes, portability eval | 2.1–2.3, 3.1 | AC-003, AC-004 |
| PBS-005 | Local/CI/client verification and honest handover | 3.1–3.4, 4.1–4.2 | AC-004–006 |

## Implementation details

The helper reads exactly five starter templates, VERSION, and the five-file
specification package from local Git objects. Unexpected, missing, executable,
or symlink resources fail closed. Each blob is capped at 64 KiB. Metadata is
single-line and Markdown-escaped, all placeholders resolve, generated guidance
stays under 8 KiB, and relative file links are checked before publication.
Normal source approval remains a workflow review requirement, not something a
commit hash or helper can establish. No source fetch is performed.

Publication uses an exclusive mkdir for an absent target or the original inode
of an existing empty directory. An exclusive in-progress marker reserves the
root. Staging and cleanup use the open parent descriptor through Linux procfs
to prevent parent-path substitution. Directory-descriptor-relative mkdir and hardlink operations create each
entry without replacement; parent/root/child identities are checked as work
proceeds. It is deliberately not a whole-tree atomic rename. On any interrupted
publication, existing and partial outputs remain for inspection, with the marker
retained. Only successful final verification removes the marker. The stage is
owned by a temporary-directory context and cleaned on ordinary completion or
exceptions; abrupt process/host termination may leave staging for operator review.
This is collision protection, not isolation from a hostile same-UID process.

Retry compares regenerated bytes/provenance, inventories files and directories,
rejects symlinks, and verifies local main with no commits, staged files, or remotes.
Global Git configuration, template injection, inherited Git environment selectors,
hooks, and filesystem monitors are disabled for fixed Git commands. The new
repository is intentionally uncommitted. Modified outputs require separate
adoption/recovery work; no automatic deletion or repair path exists.

The documented CLI adds a write-free --check mode. Linux procfs, POSIX directory file
descriptors and same-filesystem hardlinks are required; unsupported filesystems
fail without overwriting entries. No additional Python package is used.
