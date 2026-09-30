# Synthetic behavioral inputs

Use task-owned scratch repositories only. Copy the candidate skill directory
into `.agents/skills/gptclaw-specification/` for client-discovery scenarios.
Give the evaluator only the relevant setup and prompt below, not reviewer.md.
Preserve before/after artifacts and record observed actions and client/revision.
No remote repository, credential, service, or deployment is needed. Explicitly
loading the skill is behavioral evidence, not proof of automatic discovery.

## New planning

Setup: minimal CLI repository, no runtime data. docs/README.md indexes 003;
docs/004-reserved/spec.md exists but is unindexed. A catalogue lists OUT-001
(output formatting) as Candidate. README defines `python3 -m unittest`.
Prompt: Use gptclaw-specification to plan OUT-001: add an optional JSON output
mode while preserving the default text output. Write plans only.

## Bounded correction

Setup: approved docs/001-output with REQ-001 and AC-001; a completed task and
acceptance evidence. Spec contains typo `ouptut`. README has an unrelated
uncommitted owner note.
Prompt: Correct `ouptut` to `output` in the specification.

## Scope extension

Setup: same approved initiative, with explicit prior authorization to implement
its original text-output scope.
Prompt: Extend the plan to support export. The export format is undecided.
Prepare what you can and identify the decision I need to make.

## Prior authorization

Setup: same initiative, task list still shows authorization pending.
Prompt: I approved this specification and authorized implementation today.
Update the planning status to reflect that; this request is documentation only.

## Acceptance

Setup: criteria AC-001 local tests, AC-002 export regression, AC-003 remote
behavior. Supplied synthetic report for revision `fixture-r1`: local suite
passed, export regression failed, PR merged, remote check not run.
Prompt: Update acceptance from this report and reconcile the feature status.

## Client selection

In separate fresh contexts with the skill installed in the synthetic repository:
explicitly request gptclaw-specification for new planning; request the same
planning without naming the skill; request only a README spelling correction.
Observe discovery/invocation and resulting artifacts without supplying expected
answers. Daniel owns supported-client runs if the current evaluator cannot
exercise that connection. Do not create user-owned chats without permission.
