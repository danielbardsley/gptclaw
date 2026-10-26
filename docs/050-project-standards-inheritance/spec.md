# SPEC-050: Project standards inheritance

Status: Implementation authorized by the project owner on October 26, 2026.
Owner: project owner. [Design](technical-design.md) · [Tasks](tasks.md).

## Outcome and scope

New planning and application projects carry self-contained engineering standards
and the complete specification skill. The project owner's request authorizes this
GptClaw change. Dogstats and all other existing projects remain untouched.
Published application releases remain immutable. No runtime, infrastructure,
package installation or production promotion is included.

## Requirements

- PSI-001: Both planning bootstrap and catalogue application creation copy a
  bounded, versioned guidance bundle with Python, mobile and shared TypeScript/
  quality standards, a local applicability index, the complete planning skill and its local planning index/catalogue.
  Stack-neutral projects retain all references until their stack is selected.
- PSI-002: Generated root guidance requires reading applicable standards before
  implementation and mapping requirements to actual quality gates. Record
  justified adaptations and gaps explicitly; copying files is not enforcement.
- PSI-003: Record source identity and file hashes, include all resources in
  provider packaging, reject missing/unsafe resources before publishing, and
  preserve immutable releases, no-clobber creation and existing project bytes.
  The release gate must reject committed starter files missing from the copied
  application-release inventory.
- PSI-004: Test both creation paths, completeness, local references, provenance,
  missing resources and provider parity with synthetic isolated fixtures.

## Acceptance

| ID | Evidence | Requirements |
|---|---|---|
| PSI-AC01 | Planning output contains standards and skill with valid local links/hashes; unchanged retry works. | PSI-001–003 |
| PSI-AC02 | Each supported application family receives guidance and provenance; original releases remain unchanged. | PSI-001–003 |
| PSI-AC03 | Missing resources prevent publication; provider bundle contains identical resources; focused and repository checks pass. | PSI-003–004 |

Deliver a reviewable PR. Merge, installed-provider rollout and fresh-client
instruction discovery remain separate from local verification. Rollback uses a
reviewed revert and never deletes generated projects.
