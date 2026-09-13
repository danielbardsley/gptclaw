# TDD-005: Nested Guidance Pattern

- **Status:** Implemented; review and acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-005](./spec.md)
- **Implementation tasks:** [TASKS-005](./tasks.md)
- **Last updated:** 2026-09-13

## 1. Approach

Extend the existing Markdown guidance system with an inert area contract and a
manual adaptation procedure. Add one real area policy under the specification approval recorded on
2026-09-13. Reuse Bash/Python standard-library checks; no new runtime, installer,
package, client setting, or infrastructure behavior is required.

## 2. Files

| File or location | Responsibility |
|---|---|
| `templates/agents/nested/AGENTS.md.template` | Versioned area contract with explicit authoring placeholders; maximum 4 KiB. |
| `templates/agents/nested/README.md` | Placement, discovery, adaptation, review, budget, update, rollback, and acceptance procedures. |
| `templates/agents/nested/examples/*.example` | Five inert illustrations: infrastructure, mobile, backend, migrations, UI. |
| `templates/agents/README.md` | Link the area pattern from the existing root adaptation guide. |
| `AGENTS.md` | Short pointer requiring applicable area discovery before subtree work. |
| `infra/dev-host/AGENTS.md` | Concrete infrastructure specialization, derived from existing sources. |
| `scripts/tests/test_nested_agents.py` and explicit fixtures | Focused authoring checks and isolated hierarchy/rollback fixtures. |
| `scripts/check-repository.sh` | Integrate focused tests with the existing offline gate. |
| `.github/workflows/terraform-dev-host.yml` | Review path coverage and adjust only if necessary for changed guidance/tests. |
| `docs/005-nested-guidance-pattern/acceptance.md` | Actual evidence and pending acceptance, created during implementation. |

Retain `Template-Version` in reusable sources and `Source-Template-Version` plus
`Template-Source` in adoptions. Use stable sections for scope/ownership, local
conventions, commands/verification, constraints, and maintenance. Area scope is
explicit relative to the repository root; parent references resolve from the
file's directory. The guide defines the exact authoring syntax before checks
are implemented. Root SPEC-004 metadata and required sections remain intact.

## 3. Discovery and adoption flow

1. Inspect Git state and applicable instruction files, including unknown
   overrides. Read only relevant non-secret client discovery metadata.
2. Map directory ownership and durable local differences. Select the narrowest
   useful placement; avoid additional active files for illustrative stacks.
3. Compare documented startup discovery with the actual supported client.
   Inventory each accepted instruction chain and effective byte budget without
   changing global settings. Report shadowing and ambiguity for review.
4. Adapt the template, reconcile parent instructions, and add a concise root
   discovery pointer. Keep shared safeguards in the root contract.
5. Run authoring checks, existing repository checks, and semantic review.
6. Verify fresh tasks at the root and area entry points. For root-started work,
   permit read-only discovery and distinguish explicit file reads from automatic
   startup loading. A directory change alone is not evidence of a new chain.

For a cross-area task, discover guidance along each target path. Common parent
instructions apply to both; sibling-specific instructions apply only within
that sibling. A deeper fixture specializes a harmless convention explicitly.
Conflict cases must produce a clear unresolved issue while allowing unrelated
work to proceed, without inventing new permissions.

## 4. Verification design

The offline validator reads explicit policy/example inputs and checks the
contract, metadata, scoped parent/local links, placeholders, and UTF-8 sizes.
Reuse existing link-checking behavior where appropriate without requiring the
full root-template headings in area files. Do not execute commands extracted
from Markdown or implement a simulated Codex loader and call it client evidence.

Create a temporary synthetic Git project with root guidance, two distinct sibling
areas, and one deeper area. Use harmless distinct conventions and real local
references. Keep fixture sources inert in GptClaw. Negative authoring tests
cover missing sections, invalid scope/parent references, unresolved placeholders,
malformed provenance, broken links, and oversize content. A sentinel verifies
that validation does not execute embedded commands.

Remote acceptance exercises the scenarios in SPEC-005 AC-004–006. Override and
conflict cases exist only in task-owned synthetic fixtures. Record expected and
observed scope, source loading versus deliberate reads, client metadata, reviewed
revision, and relevant limits; never record secrets or raw environment/session
dumps. Unsupported remote entry points stay pending instead of being replaced
silently with local tests.

## 5. Maintenance and rollback

Version the nested contract independently of the root template. Review any root
template contract change under its existing versioning rules; an adoption-only
pointer must not falsely claim a new root template release. Changes to examples
or templates never rewrite active files automatically.

Rehearse targeted first-adoption and update reverts in isolated Git fixtures
with unrelated later commits and uncommitted notes. Reconcile conflicts and
verify the preserved files. Live changes follow the repository PR process and
fresh-task verification; no host installer or bootstrap pin is touched.

## 6. Traceability

| Requirements | Design sections | Acceptance |
|---|---|---|
| NAG-001 | 2, 3 | AC-001, AC-002 |
| NAG-002 | 3, 4 | AC-004–006 |
| NAG-003 | 3, 4 | AC-002, AC-005, AC-006 |
| NAG-004 | 2–4 | AC-001, AC-002, AC-006 |
| NAG-005 | 2, 5 | AC-002, AC-007 |
| NAG-006 | 4 | AC-003–006, AC-008 |

## 7. Implementation details

The area contract is version 1.0.0 with explicit `Area-Scope`, `Parent-Guidance`,
and `Owner` fields. The validator reuses the root validator with separate section,
placeholder, and size parameters; root defaults and its ten tests are preserved.
Parent validation requires an existing ancestor policy inside the explicit root,
and scope must match the adopted directory. Semantic parent selection, shadowing,
and instruction behavior remain human/client checks.

Five concrete examples are materialized at their hypothetical area paths so their
relative links can be checked. Fixed fixture sources add a root contract, deeper
backend area, temporary UI override, and deliberately conflicting backend rule.
The helper refuses nonempty destinations and accepts only three named scenarios.
Nine tests cover authoring failures, no execution/network/unrelated reads, inert
sources, explicit placement, and first-adoption/update rollback preserving later
committed, tracked-dirty, and untracked work. They do not simulate Codex loading.

Existing workflow filters already cover every implementation path; the workflow
was reviewed and left intact. The root pointer is an adoption-only addition; the
root canonical template and host policy/bootstrap remain unchanged.
[Acceptance evidence](./acceptance.md) separates local verification from pending
review, remote behavior, effective remote settings, CI, and merge.
