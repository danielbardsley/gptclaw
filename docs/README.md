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
  [Tasks](./002-automated-ebs-snapshots/tasks.md)

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
