# SPEC-051: Template CI security repair

Status: Implementation authorized by the project owner on October 27, 2026.
Owner: project owner. [Design](technical-design.md) · [Tasks](tasks.md).

Repair the failing quality matrix and private application workflow observed on
merged main ea8d126. Dogstats and all existing projects remain untouched.

- CI-001: Resolve high/critical dependency findings using patched compatible
  dependencies in new immutable successor releases; retain exact toolchains,
  frozen restores, security gates and historical release bytes. Do not renew
  advisory exceptions or suppress findings.
- CI-002: Explicitly retire superseded vulnerable releases from full execution,
  retaining integrity/generation coverage and a documented successor. Current
  releases remain subject to full quality and negative checks.
- CI-003: Exercise patched successors in private application integration jobs,
  retain defect rejection and expose bounded sanitized child failure diagnostics.

Acceptance: successor audits and generated gates pass (CI-001); retirement and
missing/invalid successor regressions pass (CI-002); private integration jobs and
negative checks pass with actionable failure output (CI-003). Record actual local
and CI results separately. Deliver a PR; merge, provider rollout, existing-project
adoption and infrastructure operations require their applicable authorization.
