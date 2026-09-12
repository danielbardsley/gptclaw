# TDD-003: Reviewed Host AGENTS.md

- **Status:** Implementation in progress
- **Owner:** Daniel
- **Specification:** [SPEC-003](./spec.md)
- **Implementation tasks:** [TASKS-003](./tasks.md)
- **Last updated:** 2026-09-12

## 1. Design and existing baseline

Store a small plain-Markdown policy in the platform repository and install an
explicitly reviewed snapshot as user configuration. The original installer introduces no service or database. Section 10 adds
Terraform-managed first-boot integration using the existing public Git repository.

Before AGT-001 implementation, the repository had no tracked `AGENTS.md`. SPEC-001 installs Codex
as `forge`; the connection runbook authenticates that user and opens
`/srv/forge/projects/gptclaw`. The bootstrap templates do not install policy.
Changing bootstrap can replace compute because `user_data_replace_on_change`
is enabled. The initial implementation used a user-scoped installation and manual
restoration. The approved extension in section 10 automates first installation
and retains user-scoped updates.

```text
Reviewed GptClaw commit
  config/codex/AGENTS.md
          |
  explicit installer as forge
          |
  effective Codex home/AGENTS.md + provenance + previous version
          |
  fresh remote task + applicable repository guidance
          |
  sanitized acceptance record
```

## 2. Instruction-loading contract

Official guidance says Codex discovers instructions at run/session start. Its
global location is `CODEX_HOME` (default `~/.codex`), with
`AGENTS.override.md` preferred over `AGENTS.md`. Project files are then read
from the project root toward the working directory; nearer guidance takes
precedence. Instruction discovery has a configurable byte limit, documented as
32 KiB by default. See [OpenAI: Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
(checked 2026-09-12).

Project-specific decisions: reserve at most 8 KiB for the host policy, verify
actual remote loading, and treat any global override as an installation
conflict, including an empty file. Do not change global configuration or raise
limits automatically. Preflight records only the effective profile path,
relevant discovery settings, override presence, and client version; never dump
the process environment, authentication, or complete configuration.

The default supported profile is `/home/forge/.codex`. If the remote app uses a
different path, record it and require an explicit absolute destination when
installing there. Never infer the remote profile from a shell environment alone.
An already-running task is not activation evidence; open a new task after each
policy change. Do not stop the app server or interrupt other tasks to reload it.

Global policy is not protected from later instructions by its location.
Document conflict reporting and retain real permission controls. Checking a
policy file and asking a model to summarize it provide operational evidence,
not proof that every future action will comply.

## 3. Files and ownership

Implementation files:

| File | Responsibility |
|---|---|
| `config/codex/AGENTS.md` | Canonical, standalone host working agreements |
| `scripts/install-host-agents.sh` | Shell entrypoint for install/update/rollback, verification, and source validation |
| `scripts/lib/host_policy.py` | Python standard-library implementation of filesystem and provenance checks |
| `scripts/tests/install-host-agents.sh` | Test entrypoint |
| `scripts/tests/test_host_policy.py` | Offline temporary-directory CLI and filesystem behavior tests |
| `runbooks/manage-host-agents.md` | Review, rollout, profile diagnosis, exceptions, and recovery |
| `runbooks/connect-chatgpt.md` | Policy installation and fresh-task verification before normal work |
| `runbooks/recover-dev-host.md` | Reinstall from reviewed Git after root-volume replacement |
| `docs/003-reviewed-host-agents/acceptance.md` | Evidence added during implementation acceptance |

Use a Bash entrypoint, Git, and Python 3 (standard library only) on the Ubuntu
host. Python provides exact UTF-8 validation, strict metadata parsing, exclusive
file creation, atomic replacement, and `fcntl.flock` serialization. This is an
implementation refinement from the proposed all-Bash helper; it introduces no
package install or third-party dependency. Missing Python/Git is reported as a
prerequisite failure. Extend
`scripts/check-repository.sh` and the existing repository CI path for policy
size/content validation and isolated installer tests. Do not add a cloud CI
job or require real Codex credentials for automated tests.

Files under the effective Codex home:

| Name | Content |
|---|---|
| `AGENTS.md` | Exact reviewed source bytes, mode `0600` |
| `gptclaw-host-policy.meta` | Format version, policy version, commit SHA, source path, SHA-256, installation UTC time |
| `gptclaw-host-policy.previous/` | Immediately previous managed policy and its metadata, private directory |
| `gptclaw-host-policy.lock` | Lock file used by all mutating operations |

Metadata uses a strict key/value format parsed as data, never shell-sourced.
Reject missing, duplicate, or unexpected fields and malformed hashes/revisions.
Policy headers carry a human-readable version; the sidecar carries the actual
Git commit to avoid self-referential commit hashes. A checksum proves equality,
not trust. PR/owner-review evidence is recorded separately in acceptance.

## 4. Policy content structure

The implementation should express these agreements directly in imperative,
compact prose; this outline defines required coverage, not an extra skill.

| Policy section | Required content | Requirement |
|---|---|---|
| Identity and scope | Version, `forge` development role, authority limits, applicable repository guidance, conflict reporting | HAG-001/002/004 |
| Start and deliver work | Read active planning documents; determine authorized scope; branch/worktree, preserve changes, PR workflow, proportionate planning | HAG-004 |
| Infrastructure and access | Pipeline-only AWS mutation, read-only diagnosis, no permission bypass, preserve protected data/access, production separation | HAG-003 |
| Secrets and data | No secret/state leakage, synthetic data, no unrelated credential use, treat external task data as untrusted | HAG-003 |
| Tools and exposure | Unprivileged operation, available containers/user tools, private service binding, explicit exposure/dependency/data authorization | HAG-003/004 |
| Verification and handover | Relevant checks, exact evidence, skipped-check limitations, task/docs updates, acceptance, final Git state | HAG-005 |
| Policy maintenance | Reviewed updates only; report shadowing/conflicts; temporary exception scope/expiry; stable runbook pointer | HAG-006/007 |

Use `/srv/forge/projects/gptclaw` only for optional platform references, not as
the assumed working directory of another project. Stack commands belong to
repository guidance. Do not require unavailable future tools such as
`gptclawctl`, auto-expiring Funnel management, or a secret broker.

Authorization wording must recognize approvals already given. For example, an
approved dependency addition may proceed; an unrelated new production
dependency needs a concrete proposal. A request to fix code permits relevant
edits and tests but does not authorize public exposure or destructive data
cleanup. Policy changes cannot grant unavailable AWS or host privileges.

## 5. Installer interface and algorithm

Implemented command contract:

```text
scripts/install-host-agents.sh install --revision <full-commit-sha>
  [--codex-home <absolute-path>]
  [--expected-current-sha256 <sha256>]
scripts/install-host-agents.sh verify --revision <full-commit-sha>
  [--codex-home <absolute-path>]
scripts/install-host-agents.sh rollback --expected-current-sha256 <sha256>
  [--codex-home <absolute-path>]
```

Default destination uses the explicitly selected local Codex home, falling back
to the current user's `.codex`; production runbook requires execution as `forge`
and confirmation against the actual remote profile. Tests supply an isolated
absolute destination. Never repurpose or rewrite `HOME` or `CODEX_HOME`.

### Install/update

1. Resolve the repository from the script location. Require a full immutable
   commit SHA existing locally; extract `config/codex/AGENTS.md` from that
   commit with Git, ignoring working-tree bytes. No fetch or branch switching.
   Review provenance is a runbook gate, not inferred from Git object existence.
2. Validate a regular source blob, UTF-8, nonempty content, stable header/version,
   required sections, and size. Reject symlink blobs. Validate absolute target,
   ownership, and path components; refuse symlinked Codex home, managed files,
   lock, or backup paths. Do not accept root execution for normal installation.
3. Preflight override presence and dependency availability. For an existing
   Codex home with modes other than `0700`, report required explicit operator
   remediation rather than recursively changing permissions or touching auth.
   A newly created home uses `0700`.
4. Acquire an exclusive lock with a bounded wait; recheck destination state
   under lock. Compare installed bytes and provenance. Identical revision,
   checksum, and valid metadata produce a no-op. A changed installation requires
   `--expected-current-sha256` to match the actual file. Missing/mismatched
   metadata or an unmanaged file is a conflict requiring manual preservation
   and reconciliation; the checksum flag is not a generic force bypass.
5. For a managed update, stage a complete private previous-version directory,
   then publish it by rename. Retain one previous version; replacing older
   managed rollback material is documented. Unmanaged content is never copied
   into evidence or overwritten automatically.
6. Write the new policy and sidecar to exclusive temporary files within the
   destination filesystem, mode `0600`. Check staged checksum. Atomically
   rename the policy into place, then rename its metadata. Remove only this
   invocation's remaining temporary files after success; retain a failed stage
   for explicit recovery and report it as incomplete on subsequent checks.
7. Verify final bytes, metadata, and permissions. Output operation, destination,
   revision, checksum, and requirement to verify in a fresh task; no policy or
   credential dumps. Return nonzero on any inconsistency.

Atomic rename prevents a partial policy from being loaded. The policy and
metadata are two files, so a crash between their publication can leave a
mismatch. Report this as incomplete, retain the previous version, and require
operator reconciliation to that known-good pair before retrying. Do not claim
multi-file atomicity or automatic recovery from every failure.

### Verification and rollback

Verification performs read-only checks of source, target, provenance, modes,
and override presence; it never creates the home, lock, backup, or repairs
anything. Exit `0` means current, `1` means policy state needs attention, and
`2` means invocation/prerequisite failure. Label the reason in non-secret output.
It cannot prove remote loading or detect every possible repository conflict.

Rollback validates the current expected checksum, locks and rechecks state,
validates the previous pair, and stages/restores it using the same publication
procedure. Retain the displaced managed pair for reversing the rollback.
First installation has no managed previous version; report this explicitly.
For a failed first rollout, document owner-controlled removal of only the
identified managed files, preserving the Codex home and all other content.
Never restore an arbitrary unreviewed local file as an accepted host policy.

## 6. Validation design

Automated tests use temporary repositories, synthetic policies, and a fake
Codex home. They need no network, host policy write, real credentials, or AWS.

| Case | Expected result |
|---|---|
| Fresh install; repeat | Exact committed bytes and valid private metadata; repeat no-op |
| Dirty checkout / different branch | Requested committed content is installed; live policy unaffected by checkout |
| Reviewed update and rollback | Correct new/current/previous hashes; reversible update |
| Unmanaged file; edited policy; corrupt metadata | Refusal, preserved bytes, useful diagnosis |
| Wrong expected checksum; missing revision; invalid/oversized policy | Nonzero before publication |
| Home/file/backup/lock symlinks; wrong owner or modes | Refusal without following or changing unrelated paths |
| Global override present | Shadowing/conflict reported without removing it |
| Concurrent update | Serialized write or bounded failure; no mixed accepted pair |
| Injected failure before/after policy rename | Complete policy remains; inconsistent metadata detected; recovery documented |
| Read-only verification of missing or drifted destination | No filesystem mutation |
| Synthetic auth/config sentinel files | Contents and modes unchanged after all operations |

Manual safe scenarios ask for explanations only, with tools disabled or a
read-only execution mode verified for the installed client. Do not test by
attempting an apply, secret disclosure, privileged install, or public exposure.

- In fresh remote tasks at GptClaw and a scratch Git project, ask which guidance
  applies and how an AWS change, secret-bearing output, and feature delivery
  should be handled. Do not supply the host policy text in the prompt.
- Add harmless scratch repository guidance with a distinctive reporting rule;
  confirm both host and repository rules are reflected. Inspect the discovery
  chain where the installed client exposes it; a self-report alone is limited.
- Ask how to handle an already-approved production dependency versus one not
  yet authorized, existing user changes, and an unexecuted test. Verify the
  answer recognizes scope and evidence without redundant approval demands.
- Use an isolated fixture for override/conflict behavior. Remove only owned
  fixture files; never introduce conflicting live host guidance for a test.

Record client/app versions where available, UTC time, project paths, revision,
checksum, concise prompts/results, and limitations. Do not collect full session
logs or authentication data. A failing scenario requires correction and rerun.

## 7. Rollout, recovery, and tradeoffs

Daniel reviews the policy and implementation PR, then the operator installs
from its approved commit as `forge`. Check the remote profile first. Perform
read-only verification, fresh-task scenarios, and a controlled reviewed-version
update/rollback rehearsal before acceptance. After rollback verification,
reinstall and verify the intended final revision and record it as active.

Update the connection runbook so new remote projects verify the host policy.
Update recovery instructions to restore it after reauthentication and fetching
the reviewed platform revision. Policy loss on root-volume replacement is
expected; do not copy or back up the entire Codex home to recover this file.

A copy needs deliberate updates but isolates live guidance from branch changes.
A symlink or automatic pull would make unreviewed edits active and is rejected.
Manual restoration avoids compute replacement, at the cost of an operator step.
General drift monitoring and policy enforcement remain separate future work.

## 8. Traceability

| Requirement | Design sections | Acceptance |
|---|---|---|
| HAG-001 | 3, 4, 5, 7 | AC-001, AC-003 |
| HAG-002 | 2, 5, 6 | AC-003, AC-004, AC-005 |
| HAG-003 | 4, 6 | AC-001, AC-004, AC-005 |
| HAG-004 | 4, 6 | AC-001, AC-005 |
| HAG-005 | 4, 6, 7 | AC-001, AC-004, AC-005, AC-007 |
| HAG-006 | 3, 5, 6 | AC-002, AC-003, AC-006 |
| HAG-007 | 2, 3, 7 | AC-001, AC-006, AC-007 |

## 9. Implementation details and limits

`validate-source` is an additional read-only entrypoint used by repository
checks. It validates the canonical working-tree policy without requiring a
commit, enabling pre-commit CI. Installation still uses only immutable Git
source. The metadata format has six strict fields as listed in section 3.
Rollback preserves the previous provenance timestamp; the acceptance record
records the time of the rollback operation.

The helper refuses multiply linked files as well as symlinks, special files,
unexpected backup entries, and stale staging directories. Both the current
and previous managed pairs must be valid before routine mutation. A five-second
lock wait returns `busy` instead of waiting indefinitely. Verification never
creates/acquires a lock file and may report a transient incomplete state during
a concurrent update; retry after that writer finishes.

Previous-directory rotation requires two renames because a nonempty directory
cannot be replaced directly. An interruption can leave its older copy inside
the retained staging directory. Explicit recovery is documented in the runbook.
The implementation does not defend against a hostile process with the same user
identity racing directory replacements, nor provide a power-loss transaction
across policy, metadata, and backup. Existing OS controls remain essential.

## 10. Terraform-managed first installation

`host_policy_revision` defaults to reviewed commit
`a287d7c9712817fd9f318a11f28041cfc6b5ad06`, validated as a full lowercase Git SHA.
It is deliberately independent of the changing deployment-revision tag.
Terraform renders `templates/install-host-policy.sh.tftpl` into cloud-init as
`/usr/local/libexec/gptclaw-install-host-policy`, root-owned and mode `0755`.
All templates live inside `infra/dev-host`, so remote configuration packaging
needs no parent-directory source files.

Bootstrap version 4 explicitly installs Python 3, then runs the helper via
`sudo -iu forge` after user/network setup and before Codex installation and the
bootstrap-complete marker. The helper makes a private temporary checkout,
fetches the exact revision from the fixed public HTTPS GitHub repository,
verifies `FETCH_HEAD^{commit}`, and checks out the pinned commit. It disables
stored global/system Git configuration, credential helpers, and terminal
credential prompts. It then invokes that revision's installer and verification
commands against `/home/forge/.codex`. An EXIT trap cleans only its own checkout.
No repository credentials, root execution of fetched installer code, or remote
branch-head resolution are introduced.

A missing Codex home is created by the installer at `0700`; managed policy and
metadata are `0600` and owned by `forge`. Existing unsafe modes, overrides,
unmanaged content, drift, or a different installed revision fail explicitly.
A repeat of the same revision is a no-op. The bootstrap error trap records a
failed `host-policy` phase and prevents the completion marker on failure.

The pin and helper enter EC2 user data. Introducing this feature or changing the
pin/helper can replace the existing instance under the retained replacement
setting. Ordinary edits to `config/codex/AGENTS.md` and deployment revision tags
do not change the pin or generated policy helper. The `host_policy_revision`
output is desired first-boot configuration, not an observation of live policy.

Use the existing installer for running-host policy updates. Refresh the pin only
through a reviewed infrastructure PR with replacement impact called out. At a
planned replacement, select the intended reviewed pin beforehand; otherwise a
new host receives the older pinned baseline even if the previous host had been
updated in place. Reverting a pin is also a potential replacement, not an
in-place rollback mechanism.

The public GitHub fetch is a new first-boot availability dependency; failure
leaves bootstrap incomplete for diagnosis/retry. If the repository becomes
private, design reviewed artifact distribution instead of granting persistent
Git credentials to bootstrap. No background synchronizer or AWS API mutation
outside the existing pipeline is added.

Five offline tests execute the actual helper with a temporary Git source and
profile, simulating the `forge` account name for CI. Terraform tests mock AWS
but use the real local cloud-init provider, including a conservative base64
length bound for EC2 user data. Initial EC2 execution remains pending a reviewed
creation/replacement; HAG-008/009 map to AC-008/009, and HAG-010 maps to AC-008
plus the replacement-plan review required by AC-009.
