# GptClaw documentation

Project and feature planning documents are grouped by initiative so that each
specification stays beside its technical design and any later implementation
notes.

Platform-level handover documents live together under `docs/platform/`. They
describe direction and the candidate feature backlog, but they are not
specifications and do not authorize implementation.

## Folder convention

Each initiative uses a numbered, descriptive folder:

```text
docs/
  NNN-kebab-case-name/
    spec.md
    technical-design.md
    tasks.md
```

- `spec.md` defines the outcome, scope, requirements, and acceptance criteria.
- `technical-design.md` defines the implementation architecture and maps it
  back to the specification.
- `tasks.md` provides the dependency-ordered implementation checklist and
  acceptance gates.
- Additional supporting documents may be added to the same initiative folder
  when needed.
- Cross-references within an initiative use relative links.
- New specifications and designs must not be placed in separate top-level
  `specs` or `docs/design` folders.

## Architecture decisions

[Decision index](./decisions/README.md) records durable choices, scope and owner
dispositions independently of feature implementation status.

## Initiatives

- **Platform direction:**
  [Architecture](./platform/architecture.md) ·
  [Feature catalogue](./platform/features.md)

- **001 — Bootstrap the remote development host:**
  [Specification](./001-bootstrap-remote-development-host/spec.md) ·
  [Technical design](./001-bootstrap-remote-development-host/technical-design.md) ·
  [Tasks](./001-bootstrap-remote-development-host/tasks.md)

- **002 - Automated EBS snapshots (RES-001):**
  [Specification](./002-automated-ebs-snapshots/spec.md) ·
  [Technical design](./002-automated-ebs-snapshots/technical-design.md) ·
  [Tasks](./002-automated-ebs-snapshots/tasks.md) ·
  [Acceptance](./002-automated-ebs-snapshots/acceptance.md)

- **003 - Reviewed host AGENTS.md (AGT-001):**
  [Specification](./003-reviewed-host-agents/spec.md) ·
  [Technical design](./003-reviewed-host-agents/technical-design.md) ·
  [Tasks](./003-reviewed-host-agents/tasks.md)

- **004 - Repository AGENTS.md template (AGT-002):**
  [Specification](./004-repository-agents-template/spec.md) ·
  [Technical design](./004-repository-agents-template/technical-design.md) ·
  [Tasks](./004-repository-agents-template/tasks.md) ·
  [Acceptance status](./004-repository-agents-template/acceptance.md)

- **005 - Nested guidance pattern (AGT-003):**
  [Specification](./005-nested-guidance-pattern/spec.md) ·
  [Technical design](./005-nested-guidance-pattern/technical-design.md) ·
  [Tasks](./005-nested-guidance-pattern/tasks.md) ·
  [Acceptance status](./005-nested-guidance-pattern/acceptance.md)

- **006 - Specification skill (AGT-004):**
  [Specification](./006-specification-skill/spec.md) ·
  [Technical design](./006-specification-skill/technical-design.md) ·
  [Tasks](./006-specification-skill/tasks.md) ·
  [Acceptance status](./006-specification-skill/acceptance.md)

- **007 - Project bootstrap skill (AGT-005):**
  [Specification](./007-project-bootstrap-skill/spec.md) ·
  [Technical design](./007-project-bootstrap-skill/technical-design.md) ·
  [Tasks](./007-project-bootstrap-skill/tasks.md) ·
  [Acceptance status](./007-project-bootstrap-skill/acceptance.md)

- **008 - Runtime-operation skill (AGT-006):**
  [Specification](./008-runtime-operation-skill/spec.md) ·
  [Technical design](./008-runtime-operation-skill/technical-design.md) ·
  [Tasks](./008-runtime-operation-skill/tasks.md) ·
  [Acceptance](./008-runtime-operation-skill/acceptance.md)

- **009 - Release and production-promotion skill (AGT-007):**
  [Specification](./009-release-promotion-skill/spec.md) ·
  [Technical design](./009-release-promotion-skill/technical-design.md) ·
  [Tasks](./009-release-promotion-skill/tasks.md) ·
  [Acceptance](./009-release-promotion-skill/acceptance.md)

- **010 - Session handover generator (AGT-008):**
  [Specification](./010-session-handover-generator/spec.md) ·
  [Technical design](./010-session-handover-generator/technical-design.md) ·
  [Tasks](./010-session-handover-generator/tasks.md) ·
  [Acceptance](./010-session-handover-generator/acceptance.md)

- **011 - Architecture decision records (AGT-009):**
  [Specification](./011-architecture-decision-records/spec.md) ·
  [Technical design](./011-architecture-decision-records/technical-design.md) ·
  [Tasks](./011-architecture-decision-records/tasks.md) ·
  [Acceptance](./011-architecture-decision-records/acceptance.md)

- **012 - Context validation (AGT-010):**
  [Specification](./012-context-validation/spec.md) ·
  [Technical design](./012-context-validation/technical-design.md) ·
  [Tasks](./012-context-validation/tasks.md) ·
  [Acceptance](./012-context-validation/acceptance.md)

- **013 - Versioned project manifest (PRJ-001):**
  [Specification](./013-versioned-project-manifest/spec.md) ·
  [Technical design](./013-versioned-project-manifest/technical-design.md) ·
  [Tasks](./013-versioned-project-manifest/tasks.md) ·
  [Acceptance](./013-versioned-project-manifest/acceptance.md)

- **014 - Rootless container toolchain (SYS-001):**
  [Specification](./014-rootless-container-toolchain/spec.md) ·
  [Technical design](./014-rootless-container-toolchain/technical-design.md) ·
  [Tasks](./014-rootless-container-toolchain/tasks.md) ·
  [Acceptance status](./014-rootless-container-toolchain/acceptance.md)

- **015 - Host tool profile (SYS-004):**
  [Specification](./015-host-tool-profile/spec.md) ·
  [Technical design](./015-host-tool-profile/technical-design.md) ·
  [Tasks](./015-host-tool-profile/tasks.md) ·
  [Acceptance status](./015-host-tool-profile/acceptance.md)

- **016 — Automatic Tailscale enrollment:**
  [Specification](./016-tailscale-workload-identity/spec.md) ·
  [Technical design](./016-tailscale-workload-identity/technical-design.md) ·
  [Tasks](./016-tailscale-workload-identity/tasks.md) ·
  [Acceptance](./016-tailscale-workload-identity/acceptance.md)

- **018 — First private application workflow (desktop Hello World, then repeatable apps):**
  [Specification](./018-first-private-application/spec.md) ·
  [Technical design](./018-first-private-application/technical-design.md) ·
  [Tasks](./018-first-private-application/tasks.md) ·
  [Acceptance](./018-first-private-application/acceptance.md)

## Current application milestone

[SPEC-018](018-first-private-application/acceptance.md) is merged in
[PR #40](https://github.com/danielbardsley/gptclaw/pull/40) and running on EC2.
Both independent apps are confirmed from Daniel's desktop. The shared private
Serve prefix routes subsequently started apps without per-app operator commands.
Desktop automatic source-update and managed first-app cleanup/source-retention
checks passed. Provider 1.0.1 and the resulting repair/evidence are merged in
[PR #43](https://github.com/danielbardsley/gptclaw/pull/43). This initial workflow
is Delivered. Use the [app runbook](../runbooks/manage-private-apps.md) for
operations; wider roadmap capabilities remain separate.
