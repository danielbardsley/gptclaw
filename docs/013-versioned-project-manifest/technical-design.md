# TDD-013: Versioned Project Manifest

- **Status:** Implemented, merged and accepted
- **Owner:** Daniel
- **Last updated:** 2026-09-30 (America/New_York)
- **Specification:** [SPEC-013](./spec.md)
- **Tasks:** [TASKS-013](./tasks.md)

## Approach

Implement a small Python validator and bundled JSON Schema, separate from the
future lifecycle CLI. Python 3 is the existing repository script baseline.
Use maintained YAML and JSON Schema libraries in an isolated, pinned development
environment; do not build a general YAML parser or install host packages.
T-002 selected Python 3.12, PyYAML 6.0.3 and jsonschema 4.26.0, with a complete
hash-pinned transitive lock at `requirements/project-manifest.txt`.
`scripts/setup-project-manifest.py --venv <new-directory>` creates an isolated
environment even without host pip/ensurepip. Its pinned, digest-verified pip
26.2.1 bootstrap installs wheels only. The setup and
[reference](../project-manifest.md) document exact commands and dependency pins.
Dependencies are fetched during explicit setup, never during validation.
Local verification uses `/tmp/gptclaw-prj001-venv`; CI uses a fresh runner-temp
environment with Python 3.12 from an immutable setup-python action.

The public contract remains YAML plus JSON Schema. Parsing restrictions and
cross-field rules supplement the schema; downstream consumers must use the
same validation behavior, not treat schema-only checking as equivalent.

## Version-1 fields

All fields below are required. Every object rejects additional properties.
There are no implicit defaults or optional extension bags in version 1.

| Field | Contract |
|---|---|
| `schema_version` | Integer constant `1`; boolean is not an integer |
| `project.id` | 1–48 characters; lowercase ASCII letters/digits separated by single hyphens; begins with a letter, ends with letter/digit |
| `project.name` | 1–100 characters; not whitespace-only; no control characters |
| `project.kind` | Constant `web` |
| `commands.build`, `commands.start`, `commands.test` | Arrays of 1–64 strings; executable element nonempty; each argument at most 4096 characters; no NUL/line-break/control characters; later arguments may be empty |
| `service.internal_port` | Integer 1024–65535; no allocated host port |
| `service.health.path` | Origin-relative HTTP path, 1–256 characters; starts `/`; no authority, query, fragment, backslash, percent encoding, whitespace, or dot segments |
| `service.health.timeout_seconds` | Integer 1–60; per-request timeout only, not a startup/restart policy |
| `exposure.private` | Constant `true` |
| `exposure.base_path` | Exactly `/projects/<project.id>/`; cross-field validation |
| `exposure.funnel` | Constant `false` |
| `data.mode` | Constant `ephemeral`; no platform-managed persistence |

Health path segments use ASCII letters, digits, hyphens, underscores, and dots;
reject segments equal to `.` or `..` and repeated slashes. Root `/` and a single
trailing slash are allowed. A service health path can include its application
base path. Health checks target the internal service directly; ingress paths
are not automatically prepended to it. The future routing/template design must
serve the declared base path and specify its forwarding behavior explicitly.

The checked-in `examples/project-manifest/web.yaml` is inert, not an active
`.gptclaw/project.yaml` in this repository:

```yaml
schema_version: 1
project:
  id: example-web
  name: Example Web
  kind: web
commands:
  build: [pnpm, build]
  start: [pnpm, start]
  test: [pnpm, test]
service:
  internal_port: 3000
  health:
    path: /projects/example-web/api/health
    timeout_seconds: 5
exposure:
  private: true
  base_path: /projects/example-web/
  funnel: false
data:
  mode: ephemeral
```

These are opaque argument vectors for a later executor in the repository root,
inside its reviewed runtime boundary. No shell interpolation is implied;
metacharacters are literal arguments. Validation cannot make a declared
executable safe: even an argument vector can launch an interpreter or run
malicious project code. Trust and authorization belong to the future executor.
The example assumes a future template supplies matching scripts, port behavior,
and base-path support; the validator does not claim those exist.

## Components and interface

| Component | Responsibility |
|---|---|
| `schemas/project/v1.schema.json` | Versioned structural/type constraints; local references only |
| `scripts/validate-project-manifest.py` | Thin command entrypoint over reusable parsing and validation functions |
| `scripts/project_manifest.py` | Shared validation logic, field rules, bounded parser, stable result model |
| `examples/project-manifest/web.yaml` | Inert synthetic example matching version 1 |
| `docs/project-manifest.md` | Field reference, setup, interface, author workflow and limitations |
| `scripts/tests/test_project_manifest.py` | Isolated behavioral and failure tests |
| `requirements/project-manifest.txt`, `scripts/setup-project-manifest.py`, repository checker and existing CI workflow | Hash-pinned isolated setup and execution of the same tests; no change to deployment gates |

Invocation from the GptClaw checkout:

```text
python3 scripts/validate-project-manifest.py --project-root <directory> [--json]
```

Resolve an explicitly supplied root, then read only `.gptclaw/project.yaml`
beneath it. Require the root, `.gptclaw` directory, and manifest to be
non-symlinks, including root path components; reject non-regular manifests
before reading and use no-follow/open-time checks to avoid substitution during
open. Do not scan directories or read README, package scripts, `.env`, or Git
configuration. File metadata needed for containment is permitted.

Bound the file to 64 KiB and parsed nesting to 16 levels. Reject forbidden YAML
constructs and duplicate keys before ordinary mapping construction can discard
information. Accept JSON-compatible scalar types with no implicit timestamp or
non-finite number conversion. A bounded parse must fail before recursive schema
work on excessive nesting. Treat parser diagnostics as untrusted: map them to
sanitized codes/line/column without source excerpts or raw exception strings.

Pipeline: bounded read -> restricted parse -> supported-version check ->
bundled schema -> cross-field validation -> result. Stop on parsing/version
failure; sort field errors by path then code and cap the report at 50 errors
with a truncation indicator. Never return a partially normalized manifest.
The reusable validator returns the validated mapping to a caller only on success;
the CLI exposes only a summary, not commands or raw source.

Exit codes: `0` valid, `1` invalid/missing/unreadable manifest, `2` usage,
dependency, bundled-schema, or unexpected internal failure. Human mode prints a
success summary to stdout or sanitized diagnostics to stderr. JSON mode emits
one object to stdout for handled outcomes, with `valid`, `schema_version`,
`project_id`, `errors`, and `truncated`; project ID/version are null on failure.
Errors carry `code`, `path` (JSON Pointer, or empty for document errors), and a
fixed safe `message`; parse locations are optional numeric fields. A missing
interpreter cannot produce this contract and must be reported as setup failure
by the calling environment. The lightweight entrypoint handles missing library
imports without tracebacks, including in JSON mode.

Maintain a documented error-code list including input/read/parse/limit/version,
field/type/value/unknown-field, and validator-setup/internal failures. Repeated
validation leaves source bytes untouched and gives the same ordered result.

## Verification, rollout, and limitations

Use disposable synthetic repositories, malformed manifests, and sentinel
executables/data. Prove validation never invokes the supplied command, expands
an environment variable, writes into the project, or contacts the network.
Exercise size/depth limits, duplicate keys, YAML special forms, symlink/FIFO
inputs, wrong scalar types, unknown nested fields, and semantic path mismatches.
Unreadable-file tests must exercise a real permission denial as the unprivileged
user; report unavailable checks rather than simulating a pass.

Run existing bootstrap tests to show the planning starter remains unchanged,
the new validator suite, and repository checks after implementation. Add the
necessary CI path coverage and isolated dependency setup without changing
infrastructure deployment gates. Documentation-only planning uses whitespace,
link, and traceability review; no Terraform execution is required.

Record AC-005's copy/validate/break/fix workflow and AC-006's revision/CI evidence
in a future acceptance record. There is no live-service test in this feature.
Merge publishes files only; adoption into projects is explicit. No current
manifest migration is needed because no contract has been delivered. Future
breaking versions must coexist or offer an explicitly reviewed migration.
Reverting this implementation must not delete consumers' manifests or data.

## Traceability

| Requirement | Design mechanism | Tasks | Acceptance |
|---|---|---|---|
| PMF-001 | Bundled versioned schema, strict parser, no fallback | T-002, T-003, T-005 | AC-001, AC-006 |
| PMF-002 | Required fields and command/port/path rules | T-003, T-004, T-005 | AC-001 |
| PMF-003 | Fixed private/data constraints; generated state excluded | T-003, T-004, T-005 | AC-002 |
| PMF-004 | Bounded non-executing local parser and file handling | T-002, T-003, T-005 | AC-003 |
| PMF-005 | Sanitized deterministic result and exit contract | T-003, T-005 | AC-004 |
| PMF-006 | Example, reference, author workflow, existing bootstrap checks | T-004, T-005, T-006 | AC-005, AC-006 |

Daniel approved scope and authorized implementation in T-001. T-002 pins and
setup are recorded above. Daniel accepted implementation; PR #22 merged as `aa55583`. Lifecycle APIs, runtime profiles/resource policy, actual
URL allocation, and application scaffolding remain later specifications.

## Implementation clarifications

Explicit YAML tags, including standard tags, are rejected to prevent overrides
of the JSON scalar resolver. Unknown-field diagnostics report the containing
object rather than echo arbitrary user keys. Strict integer validation rejects
floating-point whole numbers as well as booleans. The Python regex end anchor
is hardened against trailing line breaks; names/arguments also reject C1
controls and Unicode line/paragraph separators. Missing libraries, corrupt
schemas, and nonlocal schema references return setup errors without retrieval.
The CLI disables bytecode writes. See the [acceptance record](acceptance.md)
for executed evidence and limitations.
