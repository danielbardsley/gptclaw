# TASKS-015: Host Tool Profile

- **Status:** Implementation in review; deployment not authorized
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-015](spec.md)
- **Design:** [TDD-015](technical-design.md)

## Planning and decisions

- [x] T-000: Inspect catalogue, architecture, committed bootstrap and SYS-001
  boundary; draft specification/design/tasks and link the initiative.
  Evidence: source links and migration inventory in TDD-015.
- [x] T-001: Daniel reviews scope and the proposed distribution-maintained policy,
  then explicitly authorizes implementation. Recorded: “Implement SYS-004”,
  October 1, 2026 (America/New_York).
- [x] T-002: Inventory every intentional bootstrap tool and consumer; inspect only
  necessary non-secret installed metadata. Select adapter/source/version and
  verification policy per component using authoritative documentation. Resolve
  exact artifact availability or present channel exceptions with owner, reason,
  expiry and removal plan for Daniel's decision. Resolve SYS-001 integration order
  against actual merged code. Daniel approved the five existing channels through
  November 1, 2026; profile entries and runbook record ownership/removal. SYS-001
  remains a plan and installs no tools in this change.
  (HTP-001, HTP-002, HTP-005; AC-001, AC-002, AC-005)

## Implementation, after the relevant decisions

- [x] T-003: Add the versioned profile, strict schema/reference and offline
  validator. Reject unknown fields/versions, duplicate keys/IDs, unsupported
  methods/identities, unsafe arguments and conflicting package ownership before
  side effects. Preserve a single authoritative desired package list.
  (HTP-001–HTP-003; AC-001–AC-003)
- [x] T-004: Integrate fixed adapters, profile rendering/provenance, bounded checks
  and atomic sanitized receipt into existing bootstrap phases. Preserve required
  base-image parser readiness, user identities, completion gating, policy installer
  and host protections. No local installation or deployment.
  (HTP-003–HTP-005; AC-003–AC-005)
- [x] T-005: Add isolated tests for validation, injection attempts, failed sources,
  integrity/version failures, conflicts, repeated attempts, stale/partial receipts,
  retirement and phase ordering. Verify HCP upload coverage and rendered payload
  size. Run repository checks in the prepared manifest environment, shell syntax
  for changed scripts, both Git diff checks and pinned Terraform format/validate/
  test, initializing backend-free only if needed. Local checks passed; CI is
  recorded separately in acceptance.md and reviewed at T-006.
  (HTP-001–HTP-005; AC-001–AC-005)

## Review, deployment and acceptance

- [ ] T-006: Write the tool addition/update/retirement and receipt runbook, link
  recovery steps, and document rollback availability limits. Review implementation
  PR and CI before merge. Obtain Daniel's concrete deployment window/scope approval
  after reviewing the protected plan and recovery point; quiesce writes and deploy
  only through GitHub Actions/HCP Terraform. Verify persistent data and access.
  (HTP-005–HTP-007; AC-005–AC-007)
- [ ] T-007: Verify all required tools and receipt provenance on the replacement
  host; create `acceptance.md` with exact revision, sanitized evidence, source-policy
  decisions, CI/deployment links and every criterion's disposition. Distinguish
  local tests, actual host results and rollback review from an executed drill.
  Obtain Daniel's acceptance and mark SYS-004 Delivered only after merged
  implementation and passing required criteria. (HTP-004, HTP-007; AC-004, AC-007)

## Current handover

Implementation, tests and the operator runbook are complete locally. T-006's
runbook portion is complete; its review/merge and authorized deployment remain
pending. T-007's [acceptance record](acceptance.md) exists with pending deployed
criteria. No host package installation, infrastructure mutation or runtime
acceptance was performed. See the evidence record for exact checks and PR status.
