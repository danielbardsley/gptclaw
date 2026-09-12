# SPEC-004: Repository AGENTS.md Template

- **Status:** Draft; not approved for implementation
- **Owner:** Daniel
- **Feature catalogue:** AGT-002
- **Technical design:** [TDD-004](./technical-design.md)
- **Implementation tasks:** [TASKS-004](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 8–10
- **Last updated:** 2026-09-12

## 1. Summary and desired outcome

Provide a short, reusable repository `AGENTS.md` template that tells an agent
how to work in a particular project: its purpose, layout, actual stack commands,
quality gates, data rules, and product-specific constraints. Adapt it into a
root `AGENTS.md` for GptClaw as the first real adoption, and prove reuse with a
small synthetic project fixture.

An agent starting a fresh task should find concrete project guidance without
inventing commands, assuming future platform capabilities exist, or confusing
repository instructions with permission to change the host or production.

This request authorizes preparation of the planning documents. The defaults
below are proposals; implementation requires owner approval.

## 2. Scope and dependencies

### Included

- One stack-neutral Markdown template and a manual adaptation guide.
- A GptClaw root policy populated from existing repository evidence.
- Focused template/adoption checks and a synthetic portability fixture.
- Review, maintenance, rollback, and fresh-task acceptance instructions.

### Excluded

- Installing or updating the host policy, changing its bootstrap pin, or
  completing AGT-001's outstanding acceptance work.
- Nested guidance tooling (AGT-003), skills (AGT-004 onward), general context
  validation (AGT-010), manifests, project scaffolding, or repository creation.
- A catalogue of stack templates, automatic distribution to other projects,
  new quality tools, mandatory test coverage targets, or CI protection changes.
- Infrastructure, credentials, production dependencies, service startup,
  public exposure, or data migration.

[SPEC-001](../001-bootstrap-remote-development-host/spec.md) provides the
accepted repository and host foundation. [SPEC-003](../003-reviewed-host-agents/spec.md)
provides the reviewed host-policy source and installed baseline. Its
[acceptance record](../003-reviewed-host-agents/acceptance.md) still lists
fresh-task, rollback, and new-host checks as pending. Template drafting and
isolated checks can proceed independently; AGT-002 acceptance must demonstrate
repository and host guidance together on the supported connection without
claiming that this completes all of AGT-001. No future CLI, manifest, container
runtime, or skill is a prerequisite.

## 3. Proposed defaults

| Item | Proposal |
|---|---|
| Canonical template | `templates/agents/AGENTS.md.template` |
| Adaptation guide | `templates/agents/README.md` |
| First adoption | GptClaw root `AGENTS.md` |
| Template identity | `Template-Version: 1.0.0`; adopted files record their source version |
| Size budget | At most 8 KiB UTF-8 for the template and each acceptance adoption |
| Distribution | Manual adaptation in a feature branch and reviewed PR |
| Updates | Explicit project-owned edits; no automatic overwrite or synchronization |
| Additional example | Temporary synthetic Git project; no remote repository or credentials |

## 4. Requirements

### RAG-001: Complete, concise project contract

The template must cover project purpose and owner, stack/version sources,
repository layout, setup and verification commands, quality gates, planning and
delivery workflow, data handling, product constraints, and maintenance.
Essential instructions stay in the root file; detailed procedures use
repository-relative links. Mark authoring placeholders consistently and require
them to be resolved before adoption. An inapplicable section must say why;
unknown information must be an explicit limitation with an owner and next step,
not a fabricated command or an empty placeholder.

### RAG-002: Commands grounded in the actual repository

For each applicable operation, declare its command, working directory,
prerequisites, and relevant side effects: setup, development startup, build,
format/lint, type checks, tests, and other existing quality checks. State when an
operation is not applicable. Distinguish checks safe to run locally from
network-dependent setup and protected deployment operations. Version declarations
must reference the repository's existing sources rather than create competing
pins. Future architecture defaults are not installed tools.

For GptClaw, derive the command map from the README, scripts, Terraform version
file, and workflow. Preserve the GitHub Actions -> HCP Terraform -> AWS mutation
path. Do not turn planning-only or documentation-only edits into mandatory
Terraform runs; select checks according to the affected files and behavior.

### RAG-003: Clear scope and authority

Repository guidance complements the reviewed host policy with project facts;
it must not reproduce the entire host policy or claim to enforce a security
boundary. Respect higher-priority session instructions and permissions, surface
unresolved conflicts, and continue unaffected authorized work. Recognize prior
scope authorization and use proportionate planning for routine fixes.

The adoption procedure must inspect existing root and applicable area guidance,
overrides, and instruction-loading settings without reading secrets. Preserve
existing content and reconcile it in a reviewable diff. Never remove an unknown
override, change a global profile, or raise context limits automatically.
Discovery behavior must be checked against the supported client during
implementation and demonstrated in fresh tasks; file presence alone is not proof.

### RAG-004: Project-specific data and product boundaries

Require explicit entries for allowed data sources, synthetic fixtures, generated
or sensitive files excluded from Git, runtime-data locations when applicable,
and relevant product constraints. Record secret references or approved access
procedures only, never secret values. Describe private development access and
any separately governed deployment or destructive operation without granting
new authority. Projects without runtime data or a service must say so.

For GptClaw, reference existing infrastructure, credential, volume-protection,
and private-access rules. Temporary exceptions remain scoped to their original
owner, reason, expiry, and removal step; copying the template grants none.

### RAG-005: Reviewable adoption and maintenance

The template must remain inert until deliberately adapted into a repository
root policy. Include source-version provenance so maintainers can compare later
template revisions; a version match does not imply identical project content.
GptClaw adoption must preserve unrelated work and use the existing PR workflow.
Updating the canonical template must not update any adopted policy implicitly.
Document a reviewed Git revert of the adoption or later update, preserving
subsequent unrelated edits, and fresh-task verification after changes.

### RAG-006: Verification and honest evidence

Provide narrow offline checks for required sections, placeholder resolution,
UTF-8 size, source-version metadata, and local documentation references in the
shipped adoption and fixture. These checks must not execute declared commands,
fetch dependencies, read credentials, or claim to validate semantic safety.
Use human review for command correctness, applicability, and policy conflicts.

After approved adoption, fresh tasks at the GptClaw root and a temporary
synthetic project must identify their own project purpose, relevant commands,
data boundaries, and host-policy relationship without receiving policy text in
the prompt. Use explanation-only scenarios; no deployment or destructive
operation is needed. Record client/profile metadata, reviewed revision, results,
and limitations without transcripts containing sensitive material.

## 5. Acceptance criteria

| ID | Required evidence |
|---|---|
| AC-001 | Reviewed template and guide cover RAG-001–005; template and adopted files are nonempty UTF-8 within 8 KiB; adopted files contain no unresolved authoring placeholders. |
| AC-002 | GptClaw command table maps to actual scripts, version sources, and CI; applicable safe local checks pass, and skipped/network/protected operations are clearly identified. No future tool is presented as installed. |
| AC-003 | Focused offline checks pass for the adoption and synthetic fixture; negative cases detect missing sections, unresolved placeholders, oversize content, and broken local links without executing policy commands. |
| AC-004 | Review confirms existing guidance/user work is preserved, project data and product constraints are explicit, and adoption changes no host policy, credentials, infrastructure, or runtime service. |
| AC-005 | Fresh tasks through the supported remote connection in both projects correctly identify distinct project instructions and the host baseline. Missing or shadowed guidance is recorded and resolved before this criterion passes. |
| AC-006 | Guide and review demonstrate explicit template updates and a Git-based rollback in an isolated fixture, preserving unrelated edits. Record source version, owner, and fresh-task verification procedure. |
| AC-007 | Sanitized acceptance record maps all criteria to actual evidence and merged implementation PR; documentation and catalogue report the real completion state. |

## 6. Deliverables and completion

Implementation delivers the template, adaptation guide, GptClaw root policy,
focused checks/fixtures, documentation links, and an `acceptance.md` beside these
planning documents. Daniel owns review of template changes and GptClaw adoption;
other repository owners own their adaptations and updates.

Mark AGT-002 Delivered only after its implementation PR has merged and every
acceptance criterion passes. Pending remote verification remains explicit.
The feature establishes a reusable contract and one adoption; it does not claim
that every existing or future project has already adopted it.
