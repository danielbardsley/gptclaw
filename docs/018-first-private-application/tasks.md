# TASKS-018: First private application workflow

- **Status:** Draft; implementation not started
- **Owner:** Daniel
- **Specification:** [SPEC-018](spec.md)
- **Design:** [TDD-018](technical-design.md)

- [x] T-000: Refocus on the selected private-app milestone; inspect manifest,
  runtime contract and architecture defaults; run/clean up a small container smoke
  test and draft this plan. SPEC-017 remains reserved by closed unmerged PR #37.
- [ ] T-001: Daniel reviews the narrow template/workflow and authorizes
  implementation. Resolve toolchain pins, state contract, limits and routing
  capability before dependent implementation. Independent SSM access is confirmed
  by Daniel; preserve outstanding host acceptance and existing host-role bounds.
- [ ] T-002: Implement the initial CLI/template and reuse manifest validation;
  preserve existing files, define version/help/result contracts and container-only
  command execution. Verify APP-001 / AC-001.
- [ ] T-003: Implement locked lifecycle transitions, rootless service/limits,
  port reservation, bounded health/status/logs and reconciliation; test repeated,
  concurrent, occupied-port and failed-health cases. Verify APP-002/APP-003 /
  AC-002/AC-003 before dependent routing.
- [ ] T-004: Within authorized private routing scope, implement owned Serve paths,
  prefix-aware template and browser updates; preserve unrelated configuration and
  prove source edit/restart behavior. Verify APP-004/APP-005 / AC-004/AC-005.
- [ ] T-005: Run relevant repository checks and live two-project workflow from a
  tailnet client, verify scoped cleanup/source preservation, deliver implementation
  PR and record acceptance by criterion. Obtain Daniel's acceptance of this slice
  and update only the supported catalogue scope. Verify APP-006 / AC-006.

This PR delivers plans and the narrow smoke-fixture repair/evidence. It does not
implement the application runtime or publish a route. Next: Daniel reviews the
proposed first-app scope; formal logout/reboot and replacement evidence stay open.
