# TASKS-050: Project standards inheritance

Owner: project owner. [Spec](spec.md) · [Design](technical-design.md).

- [x] PSI-T00: Inspect creation paths, guidance and requirements; record the
  project owner's implementation authorization and exclusion of Dogstats.
- [x] PSI-T01: Add shared standards/skill inventory, copy through both creation
  paths, record provenance and include resources in provider bundles.
- [x] PSI-T02: Update generated guidance, specification workflow/outlines and
  creation documentation with required standards-to-gates mapping.
- [x] PSI-T03: Add completeness, failure and parity regressions; run relevant
  checks and record sanitized acceptance evidence.
- [x] PSI-T04: Publish [draft PR #107](https://github.com/danielbardsley/gptclaw/pull/107)
  and record actual CI status, limitations and Git state in acceptance.md.
- [ ] PSI-T05: Merge and installed-provider/fresh-client verification after
  applicable authorization; do not change existing projects.


## Handover

Implementation and focused verification are complete in draft PR #107. The full
local diagnostic run reported 1,000 tests with one old inventory expectation;
that expectation is corrected and its focused reruns pass. Aggregate CI is not
green because of unchanged template dependency-security findings; exact results
and the opaque legacy source-workflow limitation are recorded in acceptance.md.
No audit suppression, exception renewal, dependency upgrade or existing-project
adoption was performed. The project owner owns review, dependency-release
triage and the separately gated merge/provider/fresh-client follow-up.
