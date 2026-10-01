# Manage the development host tool profile

[SYS-004](../docs/015-host-tool-profile/spec.md) owns the
[profile](../infra/dev-host/host-tools.json),
[structural schema](../infra/dev-host/host-tools.schema.json) and
[strict validator/adapters](../infra/dev-host/lib/host_tools.py).
These declare intentionally provisioned tools, not every transitive OS package.
They do not install Podman or execute project manifests.

## Validate and review a change

From the checkout, as `forge`:

```sh
python3 -B infra/dev-host/lib/host_tools.py validate infra/dev-host/host-tools.json
```

This command is read-only and needs Python's standard library. The structural
JSON Schema is supplemented by the helper's strict types, duplicate-key rejection,
unique ownership, adapter/source/identity matching and date checks. That same
validator runs before every bootstrap phase. Full repository tests use the
[prepared manifest environment](../docs/project-manifest.md#setup-and-validation).

| Field | Version 1 contract |
|---|---|
| `schema_version` | Integer 1, not a boolean, float or string. |
| `target` | Exactly Ubuntu 24.04, amd64. Base AMI selection remains infrastructure-owned. |
| `components` | 1–100 records; unknown fields rejected throughout. |
| `id` | Unique lowercase identifier, starting with a letter, up to 64 characters. |
| `purpose`, `owner` | Nonempty bounded text naming the reason and capability owner. |
| `adapter` | `apt`, `ssm`, `aws-cli`, `tailscale`, `cloudwatch`, or `codex`; code-owned, never a command. |
| `identity` | `forge` for Codex, `root` for the other provisioning adapters. |
| `source` | Fixed approved source for the adapter; AWS exact releases use its versioned official URL. |
| `package` | A unique safe Debian package name for apt; null for specialized adapters. |
| `version.policy` | Apt: `distribution` or `exact`. AWS CLI: approved `channel` or `exact`. Remaining specialized adapters: approved `channel`. |
| `version.value` | Exact selected version or null. Existing mismatched versions fail rather than downgrade/overwrite. |
| `version.sha256` | Required lowercase SHA-256 for an exact AWS CLI archive; null otherwise. |
| `version.exception` | Channel-only owner/scope/reason/approval/expiry/removal record; null for other policies. |
| `verification` | Fixed `<adapter>-version` rule; no arbitrary probes or shell text. |

The helper reserves required bootstrap capabilities: removing one requires
reviewing its consumer and the validation contract together. Additional apt
packages can be declared without adding a second installation list. Specialized
adapters are unique and remain required while bootstrap has their consumers.
No independent package list in the bootstrap controls installation.

Before proposing a new tool, record its purpose, consuming feature, installation
identity, approved source and verification. For an apt addition use the existing
Ubuntu repositories and review dependencies. Missing apt packages must resolve
from the selected Noble version's official Ubuntu archive/security origins;
foreign candidate origins or unavailable exact versions fail. Existing satisfied
packages are observed without upgrade; their receipt is not forensic provenance.
The AMI and its configured trusted repositories remain part of the baseline.

For updates, change the reviewed profile or adapter, add tests and run the checks
below. Distribution-maintained packages and approved channels are not immutable
rebuilds. This feature neither disables nor configures OS automatic updates.
Future source changes and adapters need review; do not bypass the allowlist.

## Temporary existing-channel exceptions

Daniel approved retaining these existing sources on October 1, 2026, through
**November 1, 2026 (America/New_York)**. Validation fails from November 2 in that
zone. Expiry blocks new provisioning attempts; it does not stop running tools.
Daniel owns replacing each exception before expiry through a reviewed profile/
adapter change with a supported versioned source and verification. No automatic
extension, removal or scheduled updater is installed.

| Component | Existing source and boundary |
|---|---|
| SSM | Existing dpkg/snap installation, or explicit `amazon-ssm-agent` snap `latest/stable` fallback; no alternate fallback. |
| AWS CLI | Official current Linux x86-64 zip; no automatic overwrite of an unknown existing install tree. |
| Tailscale | Existing official installer, including its repository setup. |
| CloudWatch Agent | Existing official Ubuntu amd64 current-release deb. |
| Codex | Existing official installer, executed only as `forge`. |

These channel exceptions permit mutable upstream artifacts and their existing
installer behavior; they do not provide artifact immutability. TLS-only downloads
are bounded and installation fails on download errors. Exact AWS CLI archives
are additionally hashed before extraction or execution. Use independently
reviewed release integrity evidence when selecting a pin. Extending exact
support to another adapter requires code and tests, not an invented version URL.

Official source references for retained mechanisms:
[AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html),
[CloudWatch Agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/download-CloudWatch-Agent-on-EC2-Instance-commandline-first.html),
[Tailscale](https://tailscale.com/docs/install/linux).
Codex and SSM retain the mechanisms already declared in the baseline bootstrap;
no new source is introduced by this migration.

## Provisioning and receipt

Terraform embeds the profile and standalone helper from `infra/dev-host`, along
with the deployment Git revision, into cloud-init. They are inside the existing
remote configuration upload boundary. Cloud-init writes root-owned configuration
and helper files. The helper refuses provisioning from a source checkout and
requires the installed root bootstrap context; it is not a user install command.
Python 3 on the Noble base image is a prerequisite before any package operation.

Bootstrap clears old success markers before checking the parser or profile.
Package installation stays in its existing phases; service setup and the
independently pinned AGENTS installer retain their existing ownership. Installed
matching tools are verified without reinstallation. Incomplete/mismatched state
fails with a bounded diagnostic; no prune, autoremove or broad repair occurs.

The final phase rechecks every component before atomically publishing
`/var/lib/gptclaw/host-tools.json`. It contains schema version, canonical profile
SHA-256, deployment revision, target, observation timestamp, component versions,
identities, policy and verification status. The completion marker references the
same digest/revision. An error removes both success markers. A receipt records
tool verification at provisioning time, not ongoing drift or runtime acceptance.

Read-only inspection on an authorized host:

```sh
cat /var/lib/gptclaw/host-tools.json
cat /var/lib/gptclaw/bootstrap-complete.json
python3 /usr/local/libexec/gptclaw-host-tools validate /etc/gptclaw/host-tools-profile.json
systemctl status gptclaw-bootstrap.service
```

Compare the digest with validation of the reviewed repository profile and the
revision with the protected deployment. Avoid environment dumps, authentication
files and raw installer output. Helper failures intentionally suppress upstream
output that may contain sensitive data; use the phase and failure reason for a
scoped diagnosis. Missing versions, expired exceptions, conflicts or a failed
integrity check require a reviewed fix, not an alternate source or local sudo.

## Checks, deployment and rollback

Run `./scripts/check-repository.sh` in the prepared environment, shell syntax for
changed scripts, Git diff checks and the pinned Terraform format/validate/test
commands from repository guidance. The offline suite uses fake installers and
task-owned temporary files; Terraform tests mock AWS and use local cloud-init.
The rendered compressed payload must fit EC2's 16 KiB decoded user-data limit.
Do not run provisioning phases to test them on the active host.

A profile/helper change may replace compute. Review the protected pipeline plan,
maintenance window and adequate recovery point before requesting Daniel's specific
deployment authorization. Follow [host recovery](recover-dev-host.md), preserve
the project volume/identities, then verify SSM, private SSH, filesystem UUID,
project ownership and the complete matching receipt after replacement. Record
actual CI, deployment and acceptance evidence separately.

Retirement removes future explicit provisioning intent. Review all consumers and
tests; never uninstall from the live host automatically. A retired package may
remain in the AMI or as a transitive dependency. Rollback is a targeted reviewed
revert through GitHub Actions/HCP Terraform, potentially replacing compute again.
Check that older sources remain available and channel exceptions remain valid;
if not, prepare a reviewed alternative. Do not silently select a new version or
assume the root disk can be recovered by reverting code. Preserve project data.
