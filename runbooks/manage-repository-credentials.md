# GitHub App credentials for private projects

SPEC-023 uses one private App setup, then short-lived credentials restricted to
one managed repository. This is the reviewed setup proposal; App/installation and
live target authorization remain separate from implementation authorization.
The settings checklist is [github-app-settings.json](../config/repository-credentials/github-app-settings.json).

## Owner setup proposal

Register a GitHub App under the personal account using a unique App name. Set
visibility to **Only on this account**, disable webhooks, and leave OAuth callback
URLs empty. No public service or callback is needed. Homepage can reference the
GptClaw repository. Grant **Repository creation: write**, **Contents: write**,
**Pull requests: write**, and automatic **Metadata: read** only. Do not substitute
Administration, all repositories, a PAT or a user access token if an option is
unavailable; return the exact missing capability for review.

Install on **Only select repositories**, initially selecting only
`gptclaw-prj004-verification` (ID `1413668232`). App-created repositories should
be included automatically; live canary verification must demonstrate it.
No permission to select the platform repository or unrelated projects is implied.

Generate the App's private key in GitHub and place it through the existing private
SSH connection outside repositories, proposed path
`/home/forge/.config/gptclaw-credentials/app.pem`. The parent must be owned by forge,
mode 0700; the regular key file must be owned by forge, mode 0600, without symlink
or additional hard links. Do not paste private keys, tokens, client secrets or
JWTs in chat. Provide only App ID, installation ID and the private file path.
No client secret is needed by the proposed installation-only path.

The initial policy is private repositories with PR review without enforced branch
protection, as selected by the project owner. It has no Secrets/Environments,
Workflows or organization permission. App-created repository ownership, main
branch behavior and automatic selected-installation inclusion must be verified
before readiness is claimed. Failure never broadens privileges.

[GitHub installation behavior](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)
and [installation token scope](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
are the authority for these capabilities; local profile checks are not a hostile
same-user security boundary. Every forge process shares the development identity.
Implementation commands, rotation/revocation and recovery details follow below
as the adapter is implemented and verified.

## Implemented provider 1.5.0 interface

Use the source runner for setup and check `scripts/gptclawctl --version` first.
Older installed 1.4.0 launchers do not consume the new profile. The existing
private-app provider rollout updates the stable launcher during an authorized
app start; profile activation itself changes no service/unit/host configuration.
Owned project helpers run from an immutable 1.5.0 bundle regardless of branch
switches. Signing uses the existing `/usr/bin/openssl` implementation; no host
package or new Python crypto dependency is installed.

Prepare the private directory over the existing SSH connection, transfer the
GitHub-generated App key privately, then apply the permissions described above.
Do not put the key in this checkout or `/srv/forge/projects`.

```sh
mkdir -p /home/forge/.config/gptclaw-credentials
chmod 700 /home/forge/.config/gptclaw-credentials
# Transfer the downloaded App PEM privately to the proposed app.pem path.
chmod 600 /home/forge/.config/gptclaw-credentials/app.pem
```

These are owner setup instructions, not commands already executed by this task.
Once the exact setup is approved, configure using real IDs and the private path:

```sh
scripts/gptclawctl credentials configure \
  --app-id <app-id> --installation-id <installation-id> \
  --key-file /home/forge/.config/gptclaw-credentials/app.pem \
  --bootstrap-repository-id 1413668232
scripts/gptclawctl credentials doctor
```

Configure verifies the signed App identity, personal installation, exact minimal
grants and selected repository inventory before writing an inactive profile.
Doctor cannot establish personal creation support without the canary. It returns
`canary-required` until an actual App-created repository has completed setup;
it never treats all-repositories access or an additional privilege as a fallback.
The configuration command refuses an existing profile rather than overwrite it.

With separately authorized retained targets, perform the first creation canary:

```sh
scripts/gptclawctl credentials canary \
  --repository gptclaw-prj005-one \
  --directory /srv/forge/projects/gptclaw-prj005-one
scripts/gptclawctl credentials activate
scripts/gptclawctl new gptclaw-prj005-two --plan
scripts/gptclawctl new gptclaw-prj005-two
```

The canary proves actual installation-authenticated personal creation and automatic
inclusion before activation is permitted. Configure/activate is one setup sequence;
subsequent ordinary `new` requests use App credentials without another PAT, deploy
key or installation click. `new --plan` reports the effective private/PR policy,
roles and remote effects without publishing source; it does not return tokens.
`new --local-only` bypasses the profile entirely. Without activation, existing
normal `new` remains local-only. The initial slice supports the exact Next.js
release already delivered; it does not add templates or upgrade existing apps.

Creation uses a short-lived creation-only token inside the provisioning adapter.
Project tokens always carry exactly one repository ID and actual matching
permissions/expiry. Unexpected/omitted scope is rejected and best-effort revoked.
Automatic inclusion polls only a bounded read; denied grants are not retried with
broader permission. The default branch must read back as main; an unsupported
branch-setting path stops with retained bootstrap state rather than request
Administration implicitly. No environments, secret values, workflow writes or
public URLs are provisioned. The initial PR is opened, not merged.

## Ordinary Git and later PRs

Each generated project gets a local credential helper, a reset of inherited helper
chains, `useHttpPath=true` and `username=x-access-token`. Global Git configuration
is not changed. Exact canonical host/path/binding is checked before credential
issuance. The helper accepts bounded standard Git authentication hints without
interpreting them as authorization, and ignores store/erase rather than cache a
password. Credentials travel only through Git's pipe; no bearer convenience CLI.

```sh
git -C /srv/forge/projects/gptclaw-prj005-two fetch origin
git -C /srv/forge/projects/gptclaw-prj005-two push origin HEAD:refs/heads/codex/<reviewed-branch>
scripts/gptclawctl credentials pull-request \
  --project-root /srv/forge/projects/gptclaw-prj005-two \
  --head codex/<reviewed-branch> --title '<review title>' --body-file <owned-body-file>
```

Fetch/push obtains a fresh one-repository Contents/Metadata token. Later PR creation
uses its own Contents-read/Pull-requests-write profile. A token for A cannot be
issued for B via A's helper. Root App credentials and creation authority never
enter a Git helper or application container. No automatic push/commit/merge occurs
outside the requested provisioning or normal explicitly requested Git operation.
Dirty files, worktrees and other remotes are not reset. The helper validates the
original canonical project even when Git uses it from a worktree.

## Recovery, lifecycle and secret handling

```sh
scripts/gptclawctl credentials status
scripts/gptclawctl credentials resume --operation-id <saved-operation-id>
```

Status is local observation only and includes sanitized pending operation IDs
and bindings. Profile/bindings/receipts live under
`/srv/forge/projects/.gptclaw-runtime/v1/credentials/`, mode 0700 directories/0600
metadata files; key material stays at its external private path. No tokens are
persisted. Provisioning journals remain in SPEC-022's repositories directory.
Missing keys, wrong owner/install/grants, suspended Apps and clock/auth failures
stop safely. No host clock/security change or unrelated credential lookup occurs.

A lost create response is ambiguous: inspect the owned operation and independently
confirm private owner/operation marker and immutable ID. Only then use
`credentials resume --operation-id ... --confirm-repository-id ...`. Never adopt
by name alone or issue a second create blindly. Manual PAT operations cannot be
silently adopted by broker resume. Failed inclusion retains the repository and
journal. Partial local helper enrollment can append the same owned configuration
after a validated base config; unknown credential config or source edits stop.

Project disable serializes against credential issuance and preserves source:

```sh
scripts/gptclawctl credentials disable --project-root <canonical-project-root>
scripts/gptclawctl credentials enable --project-root <canonical-project-root>
scripts/gptclawctl credentials deactivate
```

Disable prevents new local issuance, not the use of an already handed-off token.
Enable explicitly verifies the same bound repository/grant before re-enrollment;
it never adds a GitHub installation selection. Removing a disabled project's
GitHub selection does not block unrelated enabled projects. Deactivate restores
local-only creation; owned helpers remain enrolled but refuse credentials while
the profile is inactive. No global helper or broader credential fallback is added.

API/provisioning token leases are best-effort revoked when the bounded operation
ends. Ordinary Git helper tokens must remain usable after the helper exits and
are not immediately revoked; their real expiry (normally an hour) is recorded in
non-secret receipts. Crashes and in-flight operations can leave a token valid until
that reported expiry. Owner removal of the repository grant or App uninstall has
separately reviewed effects; uninstall affects all projects. Do not claim deleting
a signing key revokes previously issued tokens.

```sh
scripts/gptclawctl credentials rotate --key-file <new-private-key-file>
```

Owner generates an additional key in the same GitHub App, transfers it privately
and invokes rotate. Identity/grants are verified before the reference switches
atomically. The old key/file is retained for owner rollback; retire it through
GitHub only after verification. Rotate back to an existing still-valid old key
when needed; no key values are logged or deleted by the broker. Signing-key
revocation/uninstall and retirement require exact operator scope and follow-through.

Rollback deactivates the profile and keeps repository history, source, bindings,
helper metadata and residual token-expiry evidence. Any helper removal or App grant
revocation is an explicit owner action, not an implicit data cleanup. The App key
is authority for all repositories selected for/created by this App; forge-owned
validation and file modes are not a boundary against hostile forge code. Preserve
private access, existing platform deploy-key isolation and production separation.
