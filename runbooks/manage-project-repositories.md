# Create a private application repository

SPEC-022 adds opt-in `gptclawctl repo` operations in provider 1.4.0. Existing
`new` stays local-only. Initial scope is `danielbardsley`, private repositories,
`nextjs@1.0.0`, protected `main` and one starter PR. This runbook is not standing
authorization to publish source, create targets or acquire credentials.

## Readiness and credentials

Use the source runner or its reviewed installed provider with the prepared
manifest environment. No `gh`, host package installation, AWS change or new
public access is needed. GitHub Pro or another supported private-protection plan
is required; `/user` readback must confirm it before creation. Unsupported plans
stop setup without public visibility or policy fallback. API version is
`2026-03-10`; actual permission/plan enforcement remains GitHub's responsibility.

Daniel approves the exact target and credential scope before apply. The
provisioning interface accepts only an explicit fine-grained PAT file owned by
`forge`, mode `0600`, a private owned parent directory (`0700`), outside project
repositories, with an explicit timezone-aware expiry no more than 48 hours away.
The expiry argument is operator-supplied metadata, not proof of GitHub's actual
expiration; GitHub still validates the token on each authenticated operation.
Never supply token values in chat, shell arguments, environment dumps or source.
Do not use the GptClaw deploy key or an unrelated project credential.

Prefer two stages:

1. A short-lived fine-grained personal-account token with **Repository creation:
   write**, where available, performs creation only. Repository-name observations
   may be incomplete with that credential; GitHub still rejects collisions. Do
   not grant account-wide administration as an implicit fallback.
2. After creation, select only the new repository in a second fine-grained token:
   **Administration: write**, **Contents: write**, **Pull requests: write** and
   automatically provided **Metadata: read**. Add **Environments: write** only for
   selected environments. For requested repository secret names, add **Secrets:
   read**; environment secret metadata uses the permissions documented by GitHub
   for that endpoint. The default no-secret path needs no Secrets permission.

If GitHub cannot provide creation-only permission, Daniel must review the exact
alternative credential scope before use. This adapter enforces a fixed account
and new target; it cannot inspect the token's full grants. Successful endpoint
calls establish only permissions for those calls, not least-privilege proof.
Refer to official [repository creation](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user),
[branch protection](https://docs.github.com/en/rest/branches/branch-protection),
[environments](https://docs.github.com/en/rest/deployments/environments) and
[secret metadata](https://docs.github.com/en/rest/actions/secrets) APIs.

To write a freshly generated token privately in an interactive host terminal:

```bash
python3 - <<'PY'
import getpass, os
from pathlib import Path
folder = Path('/home/forge/.config/gptclaw-provisioning')
folder.mkdir(mode=0o700, parents=True, exist_ok=True)
os.chmod(folder, 0o700)
path = folder / 'prj004-token'
token = getpass.getpass('GitHub token (hidden): ')
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as stream:
    stream.write(token + '\n')
print('Saved:', path)
PY
```

The writer refuses an existing file. Save the repository-specific second token
under a different filename. Revoke each provisioning token in GitHub when its
phase is finished; owner-controlled removal of its private file is separate.
These are temporary provisioning credentials, not ongoing runtime/Git access.
Record owner, target, permissions, reason, expiry and revocation follow-through
without values in the operator acceptance record.

## Preview, apply and handoff

The examples below are proposed invocations; they are not executed acceptance
results. Substitute the actual reviewed expiry and destination. Keep the plan
file outside Git with mode `0600`. Preview writes only stdout; redirecting it to
a file is the operator's explicit action.

```bash
umask 077
scripts/gptclawctl repo plan \
  --repository gptclaw-prj004-verification \
  --directory /srv/forge/projects/gptclaw-prj004-verification \
  --credential-file /home/forge/.config/gptclaw-provisioning/prj004-token \
  --credential-expires-at '<actual ISO-8601 expiry with timezone>' \
  > /tmp/prj004-plan.json
```

Read the plan before applying. It names visibility, exact provenance, branches,
protection, environments, reference names and permissions. Name checks are
provisional; apply rechecks account/name/destination and the plan digest. Existing
repositories and destinations are not adopted. No app content runs during setup.

```bash
scripts/gptclawctl repo apply --plan-file /tmp/prj004-plan.json --create-only \
  --credential-file /home/forge/.config/gptclaw-provisioning/prj004-token \
  --credential-expires-at '<actual expiry>'
```

Creation-only returns `operator-required` and exit code 1 with an immutable
repository ID and operation ID. This is an intentional handoff, not a failed
creation. Generate a second token scoped to that repository, then resume:

```bash
scripts/gptclawctl repo resume --operation-id '<operation ID from receipt>' \
  --credential-file /home/forge/.config/gptclaw-provisioning/prj004-repository-token \
  --credential-expires-at '<actual expiry>'
```

The bootstrap exception publishes only a README to `main`. Setup enforces PRs
for admins, conversation resolution, zero required approvals for a single owner,
and disabled force pushes/deletion; no nonexistent CI checks are required.
Starter publication uses content-addressed GitHub objects and an exclusive new
ref, with locally computed SHAs verified before ref creation. It never updates
an existing starter ref. Exactly one operation-owned `codex/` branch and one
initial PR are created. No automatic merge occurs. Local source is atomically
published without overwriting a destination, with an unauthenticated HTTPS
origin and separately recorded guidance adaptation provenance.

`repository-ready` means configuration/PR/source setup is verified. It does not
mean ongoing Git access, starter quality checks, runtime acceptance or PR merge
are complete. Provision per-repository ongoing access through separately approved
PRJ-005/manual scope. Run the existing starter checks and private lifecycle only
after setup; the provisioning token never enters app containers. Local branch
state starts at the initial PR head, while `main` retains the review base.

Optional `--environment development` / `--environment preview` flags create only
those selected environments, with protected-branch deployment selection and no
reviewer/wait rules. They grant no deployment authority. `--secret-reference
repository:API_KEY` or `--secret-reference development:DB_URL` declares names
only: metadata readback yields `metadata-verified` or `pending-provisioning`.
The tool never writes secret values. Empty selections perform no corresponding
API operations. Production, public visibility, arbitrary templates, imports and
CI workflow generation are unsupported.

## Status and recovery

```bash
scripts/gptclawctl repo status --operation-id '<operation ID>'
```

Status without credentials reads only the local receipt. Add the explicit file
and expiry arguments for remote observation. Status never updates the receipt,
executes app source or acquires locks. Receipt storage is
`/srv/forge/projects/.gptclaw-runtime/v1/repositories/<operation ID>/receipt.json`;
owned source/staging lives beside it until publication. Receipts record plan,
intent, ID, SHAs, settings, PR, credential metadata, retained-source path and
pending handoff; they contain no token or GitHub raw error bodies.

Resume always checks immutable ID/account/visibility, main/head SHAs, verified
protection, environment settings and PR state before writes. Denials, timeouts,
rate limits, foreign edits and source/Git metadata changes stop with retained
resources. Read `last_error` and `intent` in status. Never retry apply with a new
operation to work around partial setup. Never delete a repository, weaken
protection, reset source or force push as automatic recovery.

After a lost repository-create response, status reports a candidate ID without
adopting by name. Daniel must independently verify the candidate owner, private
visibility, creation event and operation marker in the description. Only then
resume with `--confirm-repository-id <verified ID>` plus the scoped credential.
A missing candidate after a create attempt also requires owner reconciliation;
the tool does not blindly repeat creation.

Remote object/branch/protection/environment/PR response loss is reconciled from
readback and expected SHAs. Interrupted atomic local publication is reconciled
only when expected source inventory and head prove the owned outcome. Partial
local generation/commit or manual edits can require operator review; the tool
preserves the original source and generated staging rather than overwriting it.
Inspect these paths and the actual Git history, preserve any edits, and agree a
specific repair with Daniel. A receipt records the last durable phase, not proof
that an unjournaled local step never ran.

## Release, rollback and cleanup

Provider 1.4.0 packages the adapter and askpass helper alongside the existing
CLI/catalogue; immutable `nextjs@1.0.0` assets remain unchanged. Use the existing
reviewed provider update path. Reverting to the prior reviewed provider retains
source, remote resources and journals; an older provider has no `repo` consumer.
Return to the matching provider before resuming an interrupted operation.

Retain the authorized test repository/source until Daniel explicitly authorizes
cleanup. Revoke provisioning tokens after use and record the follow-through.
Local fixture cleanup in automated tests is confined to task-owned temporary
directories. GitHub deletion, protection changes, production use and app-runtime
cleanup each need their applicable separately scoped operation. No host reboot,
IaC deployment or unrelated application restart is part of this workflow.
