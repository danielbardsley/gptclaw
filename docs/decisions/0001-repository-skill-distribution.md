# ADR-0001: Repository-scoped specification skill distribution

```adr-metadata
{
  "id": "0001",
  "title": "Repository-scoped specification skill distribution",
  "status": "Proposed",
  "owner": "Daniel",
  "recorded_date": "2026-09-30",
  "decision_date": null,
  "approval_reference": null,
  "supersedes": [],
  "superseded_by": [],
  "replacement_scope": {},
  "retirement": null
}
```

## Scope

How should GptClaw maintain its specification skill and supply it to new local
planning projects? This record covers SPEC-006/007's existing repository skill
and planning starter. It does not prescribe distribution of every future skill,
forbid global skills generally, or authorize changes to bootstrap's allowlist.
The ADR's framing is Proposed pending Daniel's review; implementation approval
for the ADR convention does not accept this text.

## Context

[SPEC-006](../006-specification-skill/spec.md) chose repository version control
and reviewed PRs for the specification skill, excluding user-wide installation.
[SPEC-007](../007-project-bootstrap-skill/spec.md) supplies only that skill and
its assets from a reviewed immutable GptClaw revision to a new planning project.
The [bootstrap helper](../../scripts/bootstrap-project.py) reads a fixed Git
object allowlist and records source revision and file hashes; a SHA alone does
not prove owner review. Created files become project-owned.

[PR #16](https://github.com/danielbardsley/gptclaw/pull/16) and
[PR #18](https://github.com/danielbardsley/gptclaw/pull/18) merged those implementations.
Their [skill acceptance](../006-specification-skill/acceptance.md) and
[bootstrap acceptance](../007-project-bootstrap-skill/acceptance.md) records
still identify fresh-client checks as pending. Those merges support the concrete
past scope, not retrospective approval of every rationale in this ADR.

## Alternatives

These tradeoffs are this record's present analysis, not a claim about a prior
owner discussion:

- Repository source plus pinned project copies: the project reviews its exact
  instructions and can adapt them; updates need deliberate per-project review.
- One globally installed shared skill: centrally maintained with less duplication,
  but individual projects depend on host/user state and shared updates.
- A live shared source reference: avoids copies, but adds an availability and
  version-resolution dependency when another project needs the instructions.

## Decision

Propose retaining the implemented SPEC-006/007 arrangement: repository-owned
source, explicit reviewed revision for bootstrap, complete allowlisted copies
and provenance in each generated planning project. Treat later updates as
reviewable project changes, preserving local adaptations. Do not silently copy
new skills or synchronize existing projects.

Daniel has not yet accepted this ADR's exact framing. Existing implementation
approvals remain valid independently; this proposal neither revokes nor broadens them.

## Consequences

Projects carry reviewable instructions and known source provenance without a
runtime dependency on the original checkout. Copies can diverge and need explicit
maintenance. Hash equality proves bytes, not semantic suitability or approval.
Repository files are guidance rather than enforcement; actual supported-client
discovery/use still needs its own evidence.

## Revisit

Reconsider if maintaining copies becomes costly, projects need centrally enforced
updates, or a reviewed distribution mechanism offers versioned availability with
clear local override/update semantics. Any broader policy needs its own scope.

## Evidence and follow-up

Daniel reviews this proposal through [AGT-009](../011-architecture-decision-records/spec.md)
and [PR #20](https://github.com/danielbardsley/gptclaw/pull/20), recording an actual
disposition before changing status. No downstream implementation is required by
this documentation proposal. SPEC-006/007 owners retain their outstanding client
acceptance actions. See the [decision index](README.md) and
[authoring guide](../../templates/decisions/README.md).
