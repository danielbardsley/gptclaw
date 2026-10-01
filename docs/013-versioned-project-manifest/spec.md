# SPEC-013: Versioned Project Manifest

- **Status:** Delivered; merged and accepted
- **Owner:** Daniel
- **Feature catalogue:** PRJ-001
- **Last updated:** 2026-09-30 (America/New_York)
- **Design:** [TDD-013](./technical-design.md)
- **Tasks:** [TASKS-013](./tasks.md)
- **Context:** [Architecture](../platform/architecture.md), sections 7, 10–12;
  [feature catalogue](../platform/features.md)

## Outcome

Give one web application a versioned `.gptclaw/project.yaml` that describes
its identity, build/start/test commands, HTTP health check, private routing
intent, and data boundary. A developer can validate this contract offline and
receive actionable errors before future runtime tooling attempts to use it.

This is the first feature toward the working-product milestone: create an app,
run it privately, open it, request a change, and see the update. PRJ-001 delivers
the contract and validator, not that entire milestone. Daniel selected this
feature and requested its specification, then approved it and explicitly
authorized implementation with “Implement the spec” on 2026-09-30
(America/New_York). Daniel subsequently accepted the implementation and authorized merge;
[PR #22](https://github.com/danielbardsley/gptclaw/pull/22) merged as `aa55583`.
See the [acceptance record](acceptance.md).
Further RES work is deferred until the working-product milestone is proven;
existing backups and host safeguards remain in place.

## Scope and dependencies

Include a version-1 contract, a repository-owned JSON Schema, an offline
validator with human and machine-readable results, a synthetic example manifest,
authoring documentation, and meaningful positive/negative tests.

Support one HTTP web service per project, commands relative to the repository
root, private path-based routing, and no managed persistent application data.
The example describes a proposed web application; it is not an application
scaffold or a claim that its commands can run on the current host.

Exclude lifecycle execution and `gptclawctl` (PRJ-002), runtime/tool installation
(SYS/RUN), framework scaffolding (TPL), route publication (NET), discovery or
port allocation, dashboard UI, GitHub provisioning, databases, runtime secrets,
production deployment, public exposure, and automatic project adoption.
Do not add an active manifest to GptClaw itself or change the existing planning
starter into a runnable template.

The existing host, guidance, and planning conventions support development of
this feature. AGT-005 supplies a planning-only starter; AGT-006 awaits a reviewed
runtime interface. Neither proves a runtime exists. PRJ-001 can be accepted
without Podman, Node, a running service, network access, or AWS changes. A future
runtime specification must define execution, lifecycle state, resource limits,
port ownership, and reconciliation before these declarations can run services.

## Requirements

### PMF-001: Versioned, strict contract

Use the fixed repository-relative path `.gptclaw/project.yaml` and integer
`schema_version: 1`. Document every allowed field, type, required value, and
constraint in a checked-in versioned schema and reference. Reject unsupported
versions, unknown fields at every object level, duplicate keys, and wrong types
without coercion or silent fallback. Version 1 has one service and one supported
kind (`web`); unsupported capabilities fail explicitly.

Publish versioned schemas with the validator so validation never needs a remote
schema fetch. Breaking contract changes require a new schema version and an
explicit migration plan. Do not rewrite existing manifests automatically.

### PMF-002: Minimal web-project declaration

Require project ID and display name; build and start argument vectors; test
argument vector; service-internal HTTP port; health path and bounded timeout;
private exposure with a base path; and an explicit no-managed-data declaration.
Commands are nonempty arrays of strings, evaluated only by a future authorized
executor from the project root. There is no shell-string shorthand, interpolation,
installation hook, environment map, or executable validation hook.

Project IDs are portable lowercase slugs; names are nonempty bounded text.
Internal ports are integers in the documented range. Health paths are local to
the service and base paths are local to the private ingress, not full URLs.
The reference must distinguish these coordinate systems and define how the
future template uses the base path. Do not require actual executables, files,
or installed dependencies merely to validate declared command arguments.

### PMF-003: Private intent and explicit data boundary

Version 1 requires private exposure and disabled Funnel. It contains no host
bind address, public URL, externally chosen host port, credentials, secret
values, environment files, external includes, or persistent-volume declarations.
Its data mode declares that managed persistent application data is unsupported.
Do not imply that this prevents arbitrary project code from writing data or
that validation can detect every secret embedded in a string.

Generated state (assigned ports, actual URLs, process/container IDs, health,
receipts, and timestamps) lives outside this source contract. A valid manifest
is neither execution authorization nor evidence of isolation, health, routing,
or installed capabilities. Later consumers must preserve those distinctions.

### PMF-004: Offline, observation-only validation

Provide an explicit-project-root entrypoint that reads only the expected
manifest and bundled schema. Treat YAML as data: accept one mapping document;
reject aliases, anchors, custom tags, merge keys, duplicate keys, and non-string
mapping keys. Bound input size and nesting before expensive schema work.
Reject symlinked manifest paths and non-regular inputs with a clear error.

Validation must not run commands, import project code, resolve environment
variables, contact the network, install dependencies, write project/generated
state, or mutate services. Missing/unreadable files, unsupported versions,
malformed input, and invalid fields return nonzero without a traceback or source
contents. Ordinary permission failures must not trigger permission changes.

### PMF-005: Useful and stable results

Provide human-readable errors and an optional structured JSON result. Both
identify a stable error code and field path where available, without echoing
manifest values or command arguments. Validity, invalid input, and validator
setup/internal failure are distinguishable by documented exit status. Results
must be deterministic for identical input and validator version.

Success means only that this manifest conforms to a supported contract. Report
the schema version and project ID on success; do not report a service as running,
healthy, routed, or trusted. Return no partly valid contract on failure.

### PMF-006: Example, compatibility, and handoff

Ship a synthetic valid web example, field reference, validation instructions,
and rejection examples. Document argument-vector semantics, repository-root
working directory, health/base-path relationship, unsupported capabilities,
version changes, and the limits of static validation.

Keep the existing planning bootstrap behavior unchanged. The future template
can adopt the example explicitly; the future CLI can reuse the validator
without inventing a competing schema. Record tests and review evidence before
marking this feature complete; live app acceptance remains a later milestone.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| AC-001 | Bundled schema, reference, and example agree; valid example and boundary cases pass. Unsupported versions, unknown nested fields, wrong types (including booleans as integers), invalid slugs/ports/paths, and empty command vectors fail deterministically. | PMF-001, PMF-002 |
| AC-002 | Public/Funnel requests, persistent-data configuration, secret/environment fields, host-port/bind fields, and generated-state fields fail. Reference accurately limits what static checks prove. | PMF-003 |
| AC-003 | Missing, unreadable, symlinked and non-regular inputs; duplicate keys; multiple documents; aliases/tags/merges; malformed YAML; oversize and excessive nesting all fail safely. Synthetic command sentinels never execute; environment sentinels are never expanded; project bytes remain unchanged; validation succeeds with network unavailable. | PMF-004 |
| AC-004 | Human and JSON outputs match documented codes/paths and exit statuses for success, invalid input, and setup failure; secret-like sentinels are absent from errors and tracebacks. No partial contract is emitted on failure. | PMF-005 |
| AC-005 | An author can copy the example into an isolated synthetic project, validate it using the documented command, introduce a bad field, and correct it using the reported location. No runtime or Node installation is needed. Existing bootstrap tests still pass unchanged. | PMF-006 |
| AC-006 | Relevant repository/validator checks and CI pass; sanitized acceptance records the revision, results, PR, and limitations. Owner review accepts the contract without claiming a running app. | PMF-001–006 |

## Completion and decisions

Daniel owns scope and contract review. Deliver implementation through a branch
and PR only after specification approval and implementation authorization.
Mark PRJ-001 Delivered after merged implementation and the criteria above pass.
Do not close AGT-006's live acceptance or claim the working-product milestone
from schema validation evidence.

Approved defaults are a single web service, argument vectors, path-based private
routing, and no managed persistent data. T-002 selected pinned parser/schema
libraries and isolated setup, recorded in the design and
[contract reference](../project-manifest.md); validation requires neither host
package installation nor a network connection.
There is no deployment or data migration in this scope. A reviewed revert can
remove the validator/schema/example; it must preserve independently authored
project manifests and cannot undo any later runtime operations.
