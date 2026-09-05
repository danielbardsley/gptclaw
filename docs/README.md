# GptClaw documentation

Project and feature planning documents are grouped by initiative so that each
specification stays beside its technical design and any later implementation
notes.

## Folder convention

Each initiative uses a numbered, descriptive folder:

```text
docs/
  NNN-kebab-case-name/
    spec.md
    technical-design.md
```

- `spec.md` defines the outcome, scope, requirements, and acceptance criteria.
- `technical-design.md` defines the implementation architecture and maps it
  back to the specification.
- Additional supporting documents may be added to the same initiative folder
  when needed.
- Cross-references within an initiative use relative links.
- New specifications and designs must not be placed in separate top-level
  `specs` or `docs/design` folders.

## Initiatives

- **001 — Bootstrap the remote development host:**
  [Specification](./001-bootstrap-remote-development-host/spec.md) ·
  [Technical design](./001-bootstrap-remote-development-host/technical-design.md)
