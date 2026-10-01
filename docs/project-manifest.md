# Project manifest version 1

PRJ-001 defines one private HTTP web service. Validation checks the declaration;
it does not create an app, install its dependencies, start a service, publish a
route, detect every embedded secret, or authorize execution. The planning starter
is unchanged. [SPEC-013](013-versioned-project-manifest/spec.md) records scope.

## Setup and validation

Use Python 3.12 on Linux with Git and standard host utilities. From the GptClaw
checkout, create a new isolated environment once:

```sh
python3 scripts/setup-project-manifest.py --venv .venv-manifest
source .venv-manifest/bin/activate
python3 scripts/validate-project-manifest.py --project-root /absolute/project/path
python3 scripts/validate-project-manifest.py --project-root /absolute/project/path --json
```

The setup helper works without host pip or ensurepip. It uses stdlib venv,
downloads the pinned pip 26.2.1 wheel, verifies its SHA-256, and runs it temporarily
to install only wheels from the complete [hash-pinned lock](../requirements/project-manifest.txt).
The environment contains PyYAML 6.0.3, jsonschema 4.26.0 and pinned transitive
libraries. Package release metadata comes from [PyPI](https://pypi.org/).
Setup is the only step requiring network access. It refuses existing destinations
and retains its new directory on failure; choose a new destination for a retry.
Do not install host packages. Activate an existing prepared environment to reuse
it. Missing dependencies produce validator exit 2 with a sanitized setup error.

Upgrade dependency pins and bootstrap URL/hash together through a reviewed PR,
regenerate hashes from the selected PyPI release files, create a fresh environment,
and rerun the validator/repository tests. Do not silently upgrade at validation
time. The [setup helper](../scripts/setup-project-manifest.py) and lock are the
version sources. CI prepares the same environment using Python 3.12.

For a disposable example, from the checkout with the environment activated:

```sh
example_root=$(mktemp -d /tmp/gptclaw-manifest-example.XXXXXX)
mkdir "$example_root/.gptclaw"
cp examples/project-manifest/web.yaml "$example_root/.gptclaw/project.yaml"
python3 scripts/validate-project-manifest.py --project-root "$example_root" --json
```

Change `timeout_seconds: 5` to `timeout_seconds: 0` in that synthetic manifest;
validation reports `field_value` at `/service/health/timeout_seconds`. Restore
`5` and validation passes. Remove only this known disposable directory when
finished. The repository example is inert and assumes future application scripts.

Run `python3 -B scripts/tests/test_project_manifest.py` for focused tests or
`./scripts/check-repository.sh` for all repository checks in the prepared environment.
No Node, pnpm, container runtime, AWS credentials, or running application is needed.

## Fields

Every listed field is required; additional properties are rejected in every
object. [The bundled JSON Schema](../schemas/project/v1.schema.json) expresses
structural constraints; the validator adds parsing and cross-field rules.
[The example](../examples/project-manifest/web.yaml) is a complete valid document.

| Field | Version-1 rule |
|---|---|
| `schema_version` | Integer `1`; strings, booleans, and floating-point `1.0` fail |
| `project.id` | 1–48 ASCII lowercase letters/digits with single separating hyphens; begins with a letter; ends with a letter/digit |
| `project.name` | 1–100 characters, not whitespace-only, no control characters or Unicode line/paragraph separators |
| `project.kind` | `web` |
| `commands.build`, `commands.start`, `commands.test` | 1–64 string arguments; first argument nonempty, later arguments may be empty; each at most 4096 characters, no controls or line breaks |
| `service.internal_port` | Integer 1024–65535; not an allocated host port |
| `service.health.path` | 1–256 characters; origin-relative path starting `/`; ASCII letters/digits/underscore/hyphen/dot segments; root and a single trailing slash allowed; no repeated slashes or `.`/`..` segments |
| `service.health.timeout_seconds` | Integer 1–60; per-request timeout only |
| `exposure.private` | Boolean `true` |
| `exposure.base_path` | Exactly `/projects/<project.id>/` |
| `exposure.funnel` | Boolean `false` |
| `data.mode` | `ephemeral`; platform-managed persistent application data unsupported |

Command arrays are opaque argument vectors for a future reviewed executor,
relative to the project root inside its runtime boundary. Shell metacharacters
and environment references are literal strings; the validator does not expand
or execute them. Even an argument vector can invoke malicious code: validation
is not an executable allowlist. Executables and referenced files need not exist.

Health probes target the internal service directly using `service.health.path`;
no ingress prefix is added. `exposure.base_path` describes the path on private
ingress. The example uses `/projects/example-web/api/health` as the service path
because its future template must serve that path itself. Future routing/template
work must specify forwarding and configure base-path support; no route is tested
or created here.

`ephemeral` is a declaration, not a sandbox. Arbitrary project code may still
write data. Environment maps, runtime secrets, persistent volumes, databases,
public URLs, bind addresses, host-port choices, installation hooks, and generated
state are unsupported. Runtime receipts, health, assigned ports and URLs belong
outside this source manifest in future runtime-owned state. Never put secrets in
command arguments or other fields; static checks cannot recognize every secret.

## Parsing and filesystem rules

Read only `.gptclaw/project.yaml` under the explicit root, plus the bundled schema
and installed validator libraries. The root, all path components, `.gptclaw`,
and manifest must not be symlinks; `..` traversal is rejected. Directory
file descriptors and no-follow opens protect lookup against symlink replacement.
The manifest must be a regular file; FIFOs/devices/directories are rejected.
No directory scanning, package-script reads, environment-file reads, executable
lookup, project imports, or generated-state writes occur.

Input is UTF-8, at most 65,536 bytes, with at most 16 nested mapping/sequence
levels (the root counts as one). Exactly one mapping document is required.
Aliases, anchors, explicit tags (including standard tags), merge keys, duplicate
keys, and non-string mapping keys fail. The explicit-tag restriction is stricter
than rejecting custom tags alone, so scalar meaning cannot be overridden.

Plain scalar resolution uses JSON spellings: lowercase `true`, `false`, `null`,
decimal integers, and finite decimal/exponent numbers. `yes`, dates, octal-like
numbers and `.nan` remain strings; no timestamps or non-finite floats are created.
Use quotes when a string resembles a boolean/number. Integer fields reject floats
and booleans. Empty YAML values are strings and do not satisfy required object or
integer types. Collection depth is checked before recursive node construction.

## Output and reusable interface

Exit `0`: supported, valid declaration. Exit `1`: missing/unreadable/invalid input.
Exit `2`: usage, dependency, schema, or internal failure. Human success goes to
stdout; human errors go to stderr. `--json` emits one result object to stdout
for handled outcomes, with no stderr. `--help` prints normal CLI help.
An unavailable Python interpreter is an environment failure outside this protocol.

```json
{"valid":true,"schema_version":1,"project_id":"example-web","errors":[],"truncated":false}
```

On failure, `valid` is false and ID/version are null. Errors contain `code`,
`path` (JSON Pointer or empty for the document), and a fixed safe `message`.
Only schema-owned field names and array indices appear in paths. Unknown-field
errors identify the containing object, not arbitrary user-supplied key names.
Parser failures identify the document without source excerpts. Messages never
echo command arguments, input values, paths supplied on the command line, or raw
exceptions. Errors are deduplicated, ordered by path/code, and capped at 50;
`truncated` reports additional errors. No partial contract is returned.

| Codes | Meaning |
|---|---|
| `input_missing`, `input_unreadable` | Missing path/file or read denial |
| `input_path`, `input_kind` | Unsafe path/symlink or non-regular manifest |
| `input_size`, `input_depth` | Input resource bounds exceeded |
| `parse`, `yaml_feature`, `document`, `mapping_key` | Malformed/unsupported YAML or mapping structure |
| `version` | Missing, wrongly typed, or unsupported schema version |
| `field_required`, `field_unknown`, `field_type`, `field_value` | Contract violation at the reported field or containing object |
| `usage`, `setup`, `internal` | Validator cannot complete; no valid contract |

The reusable `scripts/project_manifest.py` function `validate_project(root)`
returns `(summary, validated_mapping_or_none, exit_status)`. Call from trusted
platform code in the prepared environment. Reuse this complete validator rather
than replacing it with schema-only checking. Consumers must separately establish
execution authorization, capability availability, runtime isolation, routing,
resource limits and service health.

## Compatibility and rollback

Version 1 never falls back to another schema or edits input. Bundled schema
references are local-only, with no network retrieval. Breaking contract changes
require a new schema version and an explicitly reviewed migration. Adoption into
an existing project remains an explicit edit, not an automatic bootstrap change.

Rollback is a reviewed revert of these tooling files; preserve independently
authored manifests and data. Remove only an environment you created and no longer
need. Removing the validator cannot undo later runtime operations. No live app,
private-route, or AGT-006 runtime acceptance is claimed by PRJ-001.
