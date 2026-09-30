---
name: gptclaw-specification
description: Create or revise GptClaw initiative specifications, technical designs, task lists, and acceptance records. Use for selected-feature planning and evidence updates; routine fixes and general writing do not require this workflow.
---

# GptClaw specification workflow

Produce the documents needed for the requested decision, at a size proportional
to the change. A planning request ends with reviewable plans, not implementation.
A narrow correction changes only the affected text and dependent references.

## Establish context

Read applicable repository/area guidance and Git status, the documentation index,
the selected catalogue entry, and relevant existing plans and source evidence.
For GptClaw these start at `docs/README.md` and `docs/platform/features.md`.
Resolve these against the repository root, not the skill directory. Inspect
actual command/version sources when the proposal depends on them. Preserve
unrelated work. Distinguish observed facts from proposals and unknowns; example
content and catalogue entries provide neither approval nor installed capability.

Use the user's requested scope and prior session authorization. Track spec
approval, implementation authorization, review, merge, and acceptance separately.
Do not ask again for an authorization already supplied. When a material decision
is missing, ask a focused question and continue independent drafting; label
reversible assumptions. Prepare concrete reviewable work before requesting a
missing approval for a dependent action. Do not infer permission to implement,
deploy, publish, or change infrastructure from a request to write plans.

## Create a new initiative

Inspect both indexed initiatives and existing numbered directories. In GptClaw,
choose one greater than the highest number in either source and use
`docs/NNN-kebab-case-name/`. Recheck before writing; if occupied, preserve it and
choose a new number. In another repository, follow its explicit conventions.

Read the relevant outlines, then adapt them rather than copying authoring notes:

- [Specification](assets/spec.md): outcome, scope, requirements, acceptance,
  ownership, assumptions, and decisions.
- [Technical design](assets/technical-design.md): derive implementation choices
  and verification from the specification; a draft design remains a proposal.
- [Tasks](assets/tasks.md): dependency order, meaningful gates, progress, and
  requirement-to-acceptance mapping.

Keep stable requirement and acceptance IDs across the documents. Every required
outcome needs a measurable acceptance criterion and implementation/verification
tasks. Include failure, rollback, migration, data, and interface detail only
where applicable; do not invent services, commands, or operational plans to
fill an outline. Link companion documents, update the index, and mark the
selected catalogue item Draft or Planned according to actual approval history.

## Revise existing work

Read the initiative before editing. Retain requirement IDs, valid approvals,
completed tasks, and evidence. Never reuse a retired ID for a new requirement;
record supersession when relevant. Identify new scope as proposed until approved,
without invalidating unaffected decisions. Reconcile affected design choices,
tasks, acceptance criteria, and status references. Do not create a new initiative
or rewrite historical documents merely to apply the current outline.

## Record acceptance

Read the [acceptance outline](assets/acceptance.md) only when evidence is available
or acceptance tracking is requested. Map each criterion to passed, failed,
pending, or not applicable with a reason and evidence. Record actual revision,
date, commands/results, PR/CI references, limitations, and remaining owner actions.
Unverified supplied reports must be attributed rather than presented as checks
you ran. Do not turn a suggested command into an executed result.

Keep local verification, CI, deployed behavior, and owner acceptance distinct.
A passing local check or merged PR cannot establish unobserved behavior. Mark
Delivered only when the implementation is merged and all required acceptance
criteria pass. The existence of `acceptance.md` does not imply completion.

## Review and hand over

Check scope consistency, requirement/design/task/criterion coverage, links,
numbering collisions, and status against actual evidence. Remove unresolved
authoring placeholders; retain substantive unknowns with an owner and next step.
Run relevant repository checks, proportionate to the changed files. Summarize
the result, decision needed, verification, limitations, and Git state.

Maintain this package through the repository PR workflow. Daniel owns GptClaw
skill changes. A reviewed targeted revert restores a prior revision while
preserving unrelated changes; verify the restored skill in a fresh context.
Do not change global settings, overwrite unknown skills, or assume an ongoing
chat reloads updated instructions.
