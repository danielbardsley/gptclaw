# SPEC-007: Project Bootstrap Skill

- **Status:** Approved; implementation in review, acceptance pending
- **Owner:** Daniel
- **Feature catalogue:** AGT-005
- **Design:** [TDD-007](./technical-design.md)
- **Tasks:** [TASKS-007](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 7–10
- **Last updated:** 2026-09-30

## Outcome

From the GptClaw project, ask the agent to create a new local project. The new
project has its own guidance, planning convention, and repository-scoped
specification skill, so subsequent work there can produce consistent plans
without depending on the original GptClaw checkout.

This first slice prepares a project for planning. It does not promise a running
application. Daniel approved this specification and explicitly authorized implementation on
2026-09-30. Review/merge and supported-client acceptance remain separately tracked.

## Scope and dependencies

Include one GptClaw bootstrap skill, one approved stack-neutral planning
starter, safe local project creation, source provenance, and isolated tests.
Copy the complete specification skill, including all four outlines, into the
new repository. Adapt AGT-002 guidance to that project's actual purpose and
available commands. Provide a clear handoff for opening the new project and
writing its first feature specification.

Exclude GitHub repository creation/credentials (PRJ-004/005), application or
framework scaffolds (PRJ-003/TPL-*), package installation, runtime management,
project manifests (PRJ-001), deployment, public URLs, global skill installation,
and automatic synchronization of already-created projects. Existing nonempty
projects require a separate adoption request; this skill does not overwrite them.
Do not distribute the GptClaw host policy as a project policy.

Dependencies are the merged AGT-002 template and AGT-004 skill. AGT-003 supplies
optional placement guidance, but no nested policy is needed for this starter.
Their remaining acceptance checks stay separate. No container runtime, platform
CLI, language toolchain, remote credential, or new package is a prerequisite.

## Approved defaults and decisions

| Item | Approved default |
|---|---|
| Bootstrap entrypoint | `.agents/skills/gptclaw-project-bootstrap/SKILL.md` in GptClaw |
| Launch context | Invoke from GptClaw; do not require a global installation or copy the bootstrap skill into every project |
| Destination | Explicit project name/slug and path; suggest `/srv/forge/projects/<slug>` when permitted by the session |
| First approved starter | Stack-neutral planning repository; no application source or runtime |
| Required inputs | Project name, purpose, owner, destination; infer supplied values without asking twice |
| Git | Initialize local repository on `main`; leave generated files uncommitted for review; no remote |
| Skill distribution | Copy the approved specification skill and assets from an immutable GptClaw revision |
| Initial documents | README, adapted AGENTS.md, .gitignore, docs/README.md, docs/platform/features.md, and bootstrap provenance |
| First feature | Create plans only if requested with sufficient scope; otherwise hand off a ready planning repository |

The approved scope ships a planning starter now; a runnable stack template
remains a later feature. See [acceptance](./acceptance.md) for actual evidence.

## Requirements

### PBS-001: Clear scope and authorization

Select the bootstrap skill for creation of a new local project, not ordinary
feature work or modification of an existing project. Inspect relevant guidance,
source revision, destination, installed tools, and Git state. Explain the concrete
files and side effects. Honor authorization already supplied by a request to
create that project; ask only for missing scope or required permissions.
Creating a plan does not authorize creating its target project.

### PBS-002: Preserve existing data and contain writes

Accept an absent destination with a valid parent or an existing empty directory.
Reject nonempty destinations, symlink destinations, unsafe slugs, path traversal,
and destinations nested inside an existing Git repository. Canonicalize and show
the target before writing; do not follow symlinks into unexpected locations or
broaden permissions after a denial. Recheck at publication to avoid overwriting
concurrent work. On error, preserve pre-existing paths and user data. Retries must
recognize completed output without rewriting it, or report a concrete conflict.
Never reset, clean, or recursively delete an uncertain destination to retry.

### PBS-003: Self-contained project guidance and planning

Generate a concise README stating purpose, owner, planning readiness, and what
is not yet configured. Adapt AGT-002's six-section root guidance, resolve all
authoring placeholders, retain its size budget, and reference only files present
in the new project. Record unavailable stack commands as not configured rather
than fabricating them. Include appropriate local/generated/secret Git exclusions
without implying .gitignore is a security boundary.

Create a documentation index explaining the numbered initiative convention and
an initially empty candidate catalogue. Do not copy GptClaw's feature backlog,
approvals, deployment instructions, or acceptance results. Start numbering at
001 for the new project's first requested initiative. Routine edits remain small.

### PBS-004: Distribute a complete, versioned specification skill

Copy `.agents/skills/gptclaw-specification/` and its referenced assets from a
reviewed immutable source revision. The resulting workflow must operate using
the new project's guidance/index/catalogue without an absolute GptClaw path or
network fetch. Preserve normal automatic selection and explicit invocation.
Record source repository/revision, starter identity/version, and copied-file
hashes in a non-secret provenance file; adapted files need not match source bytes.

Do not copy authentication, settings, Git metadata, unrelated skills, overrides,
or the entire source workspace. Future updates are explicit reviewed project
changes, preserving local adaptations; no background synchronization is included.

### PBS-005: Verify and hand off honestly

Verify generated files, placeholder resolution, local references, skill assets,
provenance, and local Git boundary without running arbitrary template commands.
Report exact path, created files, checks, source revision, Git state, and next
step. Distinguish planning-ready from build-ready or remotely published.

In the new project's supported client context, demonstrate discovery and use of
the copied specification skill to create a synthetic first initiative. Prove
that no source-checkout access is needed. Record unavailable client checks as
pending rather than treating copied files as proof. Do not open user-owned chats
without an explicit request.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Reviewed skill and starter create the declared planning-only files and correctly scoped root guidance from supplied project metadata; no GptClaw-specific operational claims or unresolved placeholders leak into output. | PBS-001, PBS-003 |
| AC-002 | Positive tests for absent/empty destinations and negative tests for occupied, symlink, traversal, nested-repository, and changed-at-publication cases preserve all prior bytes; failed runs/retries do not erase user work. | PBS-002 |
| AC-003 | Generated repository contains the complete specification skill with valid links and matching source hashes; no source Git metadata, auth/settings, unknown skills, or absolute source dependency. | PBS-003, PBS-004 |
| AC-004 | Isolated behavioral evaluation produces coherent docs/001-* plans from the copied skill using only the new project; original source unavailable to the evaluator; no app implementation or external mutation. | PBS-004, PBS-005 |
| AC-005 | Supported-client fresh-context discovery and a relevant implicit planning request use the copied skill successfully; explicit invocation also works. Evidence records client, source revision, outputs, and limitations. | PBS-005 |
| AC-006 | Relevant repository tests/CI pass; provenance, failure/retry/update procedure, and sanitized acceptance record identify actual checks, merged PR, and remaining actions. | PBS-001–005 |

## Completion

Daniel owns the starter and bootstrap skill review. Deliver through a feature
branch and PR. Mark Deployed when the implementation is merged and available;
mark Delivered after all required acceptance passes. A supported-client check
may also contribute evidence to AGT-004 only when its particular criterion is
actually exercised; do not close earlier initiatives by implication.
