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
