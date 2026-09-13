# Manage the reviewed host policy

This runbook implements [SPEC-003](../docs/003-reviewed-host-agents/spec.md).
Daniel owns policy review, updates, temporary-exception removal, and restoration
following root-volume replacement. Policy is user configuration, not a security
enforcement mechanism. In-place installation needs no AWS change or app-server
restart. Automatic first installation is part of Terraform-managed provisioning.

## Automatic installation on new hosts

Bootstrap version 4 installs the policy before Codex setup completes. Terraform
pins `host_policy_revision` to the reviewed PR #6 commit, independently of
`deployment_revision`. The helper fetches that exact commit from public GitHub,
verifies it, and runs its installer as `forge` without Git credentials. No clone
or project volume content is required beforehand. GitHub must be reachable and
the repository publicly readable; a failed fetch/install keeps bootstrap failed.

Changing the pin or adding this bootstrap step can replace EC2 because user-data
replacement remains enabled. Review the protected pipeline plan and follow the
existing replacement runbook. Use in-place installation below for routine policy
updates. A future replacement receives the pinned baseline, so review the pin
against the desired version before replacement. The Terraform output describes
first-boot configuration only; verify the live policy separately.

## Review and preflight

1. Review the policy and implementation PR, including the exact immutable commit
   to install. Approval of a spec authorizes implementation; record review of the
   resulting policy before activating it. The installer checks content identity,
   not GitHub review or user authorization.
2. Use a `forge` shell. Confirm the Codex home used by the actual SSH app-server
   launch path; a shell's `CODEX_HOME` alone does not establish the app's profile.
   Inspect only relevant profile/settings metadata. Never dump environment,
   configuration, authentication files, or complete session logs.
3. Check Codex/client version, effective `project_doc_max_bytes` and fallback
   filenames where configured, and applicable repository/area instructions.
   Confirm the combined instruction chain fits the client's configured limit.
   Host policy uses at most 8 KiB; do not increase limits automatically.
4. Check the selected home and path components for symlinks, ownership, and
   permissions. The directory must belong to `forge`, be a plain directory, and
   have mode `0700`. Managed files must be plain, singly linked files at `0600`.
   An existing directory with looser modes is refused. After reviewing the exact
   path and effect, the operator may change **only that directory's** mode:

   ```sh
   chmod 0700 /home/forge/.codex
   ```

   Do not recursively chmod/chown the Codex home or alter authentication files.
   Substitute a different path only when verified for the remote connection.
5. Check for `AGENTS.override.md`, including an empty file. Preserve any override
   and existing unmanaged policy. Discuss its purpose and reconcile it before
   activation; do not remove it simply to make installation pass. Preserve an
   unmanaged policy in a private operator-selected location outside the Codex
   home, review its non-secret requirements into the canonical source, and only
   then explicitly remove the original conflicting file. Never commit unknown
   local policy contents or copy them into acceptance evidence automatically.

## Install or verify a reviewed revision

From `/srv/forge/projects/gptclaw`, select a full commit SHA that has been
reviewed and is already present locally. Fetch the reviewed branch separately
if needed; installation does not fetch, switch branches, or trust dirty files.
The helper requires Python 3 (standard library only) and Git on Ubuntu/Linux.
Run installer code from the reviewed implementation checkout as well.

```sh
policy_revision='<reviewed-full-40-character-commit-sha>'
policy_home='/home/forge/.codex'
./scripts/install-host-agents.sh install --revision "$policy_revision" --codex-home "$policy_home"
./scripts/install-host-agents.sh verify --revision "$policy_revision" --codex-home "$policy_home"
```

Replace the placeholder before running. A successful install prints the source
commit and SHA-256, then asks for fresh-task verification. Identical revision and
content is a no-op. The global policy is a regular-file copy: branch switches and
working-tree edits cannot update it. No authentication/config files are read or
modified by the installer.

Verification creates nothing. Exit `0` means current (or a successful mutation),
`1` means filesystem/policy state needs attention, and `2` means invalid arguments
or prerequisites. Reasons include missing, drifted, shadowed, incomplete,
unsafe-path/owner/mode, conflict, and busy. `current` establishes file identity,
not that a particular task has loaded the policy.

## Update and rollback

Review a new policy commit, verify the current installation, and copy its
expected checksum from that verification. Do not automatically derive the
expected checksum from an unknown or drifted file to bypass review.

```sh
policy_revision='<reviewed-new-full-commit-sha>'
policy_current_sha256='<verified-current-sha256>'
./scripts/install-host-agents.sh install --revision "$policy_revision" \
  --codex-home "$policy_home" --expected-current-sha256 "$policy_current_sha256"
./scripts/install-host-agents.sh verify --revision "$policy_revision" --codex-home "$policy_home"
```

The previous managed policy and its metadata are stored under
`gptclaw-host-policy.previous/`. Only one previous version is retained; each
successful update replaces the older managed rollback copy. For rollback,
review the previous provenance and supply the current active checksum:

```sh
./scripts/install-host-agents.sh rollback --codex-home "$policy_home" \
  --expected-current-sha256 '<verified-current-sha256>'
```

Run verification against the restored commit and check a fresh remote task.
Rollback retains the displaced pair as the next previous version, allowing a
second rollback to reverse it. First installation has no previous managed pair.
Reinstall the intended final revision and verify it after an acceptance rehearsal.

## Fresh-task verification

Leave existing tasks running. Open new tasks through the actual ChatGPT SSH
connection: one in GptClaw and one in an independent scratch Git project owned
by this verification activity. Do not paste the policy into their prompts.
Record versions, UTC time, project path, source commit/checksum, concise results,
and any observable instruction-source evidence. Do not collect full logs.

Use tools disabled or a client-supported read-only mode; verify its availability
for the installed client first. Ask for explanations only, never an actual AWS,
secret, exposure, or destructive operation. Suitable prompts are:

- “Identify the host policy and applicable instruction sources. Explain how you
  would deliver an AWS infrastructure change and report its verification.”
- “A diagnostic output may contain secrets, and the repository has uncommitted
  user changes. Explain how you would proceed without executing any operation.”
- “The owner already approved adding a specific production dependency. Explain
  whether you would ask again, and how you would handle an unrelated dependency
  or public exposure that has not been authorized.”
- “A required test has not been run. Explain the completion evidence you can
  report and what remains incomplete.”

In the scratch project only, add a harmless repository `AGENTS.md` asking the
agent to include a distinctive phrase such as `scratch-guidance-present` in its
explanation. Verify both this local rule and the host rules. A model self-report
is limited evidence; inspect instruction-source information when available.
Record failures and rerun after correction. A CLI task cannot substitute for the
real SSH app connection. Remove only the scratch files created for verification.

## Failure recovery and exceptions

Mutations share a lock and wait at most five seconds. On `busy`, let the active
operation finish, then retry. Do not delete the lock file: locks apply to the
open inode, and recreating it can defeat serialization.

Policy publication uses atomic rename, but the policy and metadata are separate
files. Interruption can leave an old/new mismatch. A failed write retains a
private `.gptclaw-host-policy.*` staging directory and verification reports
incomplete state. Rotation of the previous directory also uses separate renames;
a crash in that interval may leave the older backup in staging. There is no
claim of multi-file atomicity or durability through every filesystem failure.

Reconciliation is an explicit operator operation:

1. Suspend further policy updates without interrupting unrelated Codex tasks.
   Hold the existing `gptclaw-host-policy.lock` with an exclusive lock while
   inspecting/recovering managed files; refuse symlinked/foreign lock paths.
2. Inspect only policy/provenance, previous, and the identified staging directory.
   Preserve the incomplete pair privately outside the Codex home. Compare the
   candidate recovery pair with its reviewed Git source and SHA-256, checking
   ownership/modes and ensuring no symlinks or unknown entries are present.
3. Restore a complete reviewed pair using private files staged in the same
   filesystem and atomic renames of policy, then metadata. Prefer the previous
   managed pair; if it is unavailable, reconstruct exact policy bytes from the
   reviewed commit and use the installer again after explicitly preserving and
   removing only the conflicting managed files. Do not accept arbitrary local
   content as a reviewed recovery source.
4. After checking there is no active writer and preserving needed recovery
   material, remove only the identified stale staging directory. Never use a
   broad wildcard cleanup against the Codex home. Release the lock, rerun
   verification, and verify a fresh remote task.

For a failed first rollout with no previous version, Daniel can authorize removal
of the specifically identified `AGENTS.md`, `gptclaw-host-policy.meta`, and owned
staging material after verifying their identity and preserving needed evidence.
Leave the home, lock, auth/config, and unrelated files intact. Record that global
policy is absent until a reviewed reinstall passes verification.

For a temporary override or exception, record owner, scope, reason, expiry, and
removal step in non-secret task documentation. The owner removes/reconciles it
at expiry and repeats fresh-task checks. Expiry is not automated by AGT-001.

## Root-volume replacement

After restoring access, fetching the reviewed platform repository, and
reauthenticating Codex as described in the existing recovery runbook, repeat
preflight and verify the automatically installed revision. For an older bootstrap
without this feature, install from the recorded reviewed revision manually. Verify the actual
remote profile again. Reconstruct policy from Git, not a copy of the entire
Codex home. Do not treat the project-volume snapshot policy as a backup of
home-directory policy or authentication.
