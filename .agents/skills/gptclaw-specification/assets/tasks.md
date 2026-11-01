# Implementation tasks outline

Authoring aid: record status, owner, date, and specification/design links. Use
stable task IDs and checkboxes; checked tasks need actual supporting evidence.

## Planning and authorization

Record completed discovery and drafting, remaining scope decisions, and actual
specification approval/implementation authorization. Honor approval already
supplied; do not insert a repeat approval task.

## Implementation

Group concrete tasks in dependency order. State prerequisites and meaningful
phase gates. Include task-to-requirement and acceptance mappings here or in a
compact traceability table. Keep pending tasks unchecked.

## Verification and delivery

Include relevant checks, behavioral acceptance, evidence recording, review/PR,
merge, status updates, and cleanup of owned fixtures. Separate implementation
completion from acceptance that needs a different environment or operator.

For products adapted from application starters, include a starter adaptation
review: remove demo-only code/content outside the product spec, update dependent
registrations/imports/API schema/docs/tests, and verify the resulting product API
and UI. Record any spec-required retained demos and preserve user data.

## Current handover

Summarize completed work, evidence, remaining tasks, limitations, and the next
action/owner. Keep earlier acceptance records and unaffected approvals intact.

For a project with inherited engineering standards, identify applicable references
and map their formatter/lint, typing, tests/coverage, security, build and CI
requirements to implemented commands and verification. Record justified
adaptations and gaps with rationale, owner and review status; do not treat copied
files or passing unit tests as proof that all required gates exist.

For application delivery, name the principal user journey and a bounded first
real demonstration milestone. Order implementation tasks to enable and verify
that journey early. Defer speculative edge cases, broad refactors and optional
polish with a reason and revisit trigger; reprioritize repeated hardening without
journey progress. Fix observed blockers and retain required security, privacy,
data-integrity and acceptance gates. Isolated tests cannot close the journey
milestone; core journey evidence does not replace full acceptance.
