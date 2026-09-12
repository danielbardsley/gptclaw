# TDD-004: Repository AGENTS.md Template

- **Status:** Draft; pending specification approval
- **Owner:** Daniel
- **Specification:** [SPEC-004](./spec.md)
- **Implementation tasks:** [TASKS-004](./tasks.md)
- **Last updated:** 2026-09-12

## 1. Approach and baseline

Use a plain Markdown source with explicit authoring placeholders, a manual
adaptation guide, and one real adoption. No generator, installer, daemon, or
new package dependency is needed. The template filename deliberately differs
from active `AGENTS.md` guidance. It is a reusable document, not a project
scaffold or a replacement for the host policy.

At drafting, GptClaw has no root `AGENTS.md`; its canonical host policy is
`config/codex/AGENTS.md`. Existing command sources are `README.md`,
`scripts/check-repository.sh`, `.github/workflows/terraform-dev-host.yml`, and
`infra/dev-host/.terraform-version`. Recheck this baseline before adoption.

## 2. Proposed files and content

| File | Responsibility |
|---|---|
| `templates/agents/AGENTS.md.template` | Stack-neutral contract with `{{UPPER_SNAKE_CASE}}` authoring placeholders and template version. |
| `templates/agents/README.md` | Adaptation checklist, placeholder meanings, command evidence, review, update, and rollback procedures. |
| `AGENTS.md` | Fully adapted GptClaw guidance, version provenance, and relative links to existing documentation. |
| `scripts/tests/test_repository_agents.py` | Standard-library offline checks and synthetic positive/negative fixtures. |
| `scripts/check-repository.sh` | Run focused checks alongside existing repository checks. |
| `.github/workflows/terraform-dev-host.yml` | Add root-policy/template path triggers to existing quality workflow; retain manual protected plan/apply behavior. |

Use stable sections: Project and ownership; Stack and layout; Commands and
quality gates; Planning and delivery; Data and product constraints; Guidance
maintenance. The command table includes operation, working directory, command
or explicit not-applicable explanation, prerequisites/side effects, and when
to run it. Keep core instructions short and link to existing procedures.

GptClaw's adoption points to the initiative index rather than permanently
naming one active feature. Its validation guidance distinguishes documentation,
host-policy/scripts, and Terraform changes. Deployment instructions identify
the protected workflow without offering a local apply command. Inspect version
sources rather than duplicating version numbers.

## 3. Adoption flow

1. Inspect Git state and applicable instructions. Locate existing root/area
   policies and overrides; inspect only relevant non-secret discovery settings.
2. Recheck supported-client discovery documentation and actual configuration.
   Record discrepancies without changing global policy or settings. Respect
   the proposed 8 KiB per-file budget and inspect the effective combined budget;
   a size check alone cannot prove loading.
3. Build the project fact/command map from checked-in sources. Classify each
   operation's prerequisites and side effects before considering execution.
4. Adapt the template in a feature branch. Reconcile any existing root policy
   manually; retain project-specific rules and explain intentional changes.
5. Run offline content checks and relevant existing project checks. Review the
   result for applicability, authority, and data-handling correctness.
6. After approval, verify the adopted revision in fresh tasks through the
   supported connection and record acceptance evidence.

The guide must work outside the GptClaw checkout using repository-relative
references in adopted files. Host-policy optional references remain owned by
SPEC-003; no duplicate installed policy is introduced.

## 4. Validation and fixtures

Use Python's existing standard-library test pattern. Checks read the canonical
template, adopted policy, and explicit fixture files; do not recursively scan
unrelated projects. Verify fixed required headings, template/source version
metadata, UTF-8 byte limits, resolved placeholders in adopted files, and local
file-link targets. Define supported link syntax in the test/guide; do not claim
a general Markdown validator or resolve external links over the network.

The temporary synthetic Git project has a distinct purpose, synthetic-data
rule, a harmless standard-library verification command, and real referenced
files. It needs no GitHub repository, new credentials, package installation,
service, or infrastructure. Negative fixtures remove a required section, leave
a placeholder, exceed the byte budget, or reference a missing file. A command
sentinel demonstrates that validation never executes text in the policy.

Human review verifies the GptClaw command map against source and confirms
not-applicable entries are justified. Remote acceptance asks each fresh task to
explain project purpose, checks for a documentation versus behavior change,
data rules, and the boundary between repository guidance and host agreements.
Prompts must not supply the answers. Only task-owned fixtures are cleaned up.

## 5. Updates, rollback, and limitations

A template version identifies the starting contract; each adoption remains an
independent project-owned file. Compare later template revisions, incorporate
relevant changes in a reviewed PR, and update provenance deliberately. No
background synchronization or automatic replacement is allowed.

Rehearse adoption/update rollback in the temporary Git project using a targeted
revert; retain unrelated later edits and resolve conflicts explicitly. Live
rollback follows the same reviewed repository workflow and requires a fresh
task to observe restored instructions. Existing tasks are not reloaded.

Static checks cannot establish instruction compliance, semantic command safety,
or actual remote loading. AGT-001's pending acceptance remains separate. The
existing workflow may run its full quality job when template paths change;
local check selection remains proportionate and no plan/apply is dispatched by
these path additions.

## 6. Traceability

| Requirements | Design | Acceptance |
|---|---|---|
| RAG-001 | Sections and placeholders, file budgets | AC-001, AC-003 |
| RAG-002 | Evidence-based command map and check selection | AC-002 |
| RAG-003 | Preflight, reconciliation, fresh-task checks | AC-004, AC-005 |
| RAG-004 | Explicit project data/product entries and review | AC-004, AC-005 |
| RAG-005 | Manual adaptation, version provenance, targeted rollback | AC-001, AC-006 |
| RAG-006 | Offline tests, human review, sanitized remote evidence | AC-003, AC-005, AC-007 |
