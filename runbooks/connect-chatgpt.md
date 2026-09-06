# Connect ChatGPT to the development host

Use this runbook only after the GitHub/HCP pipeline has deployed the host and
AWS Systems Manager access has been verified.

## 1. Prepare the desktop

1. Sign the Windows desktop into the approved Tailscale tailnet.
2. Confirm ChatGPT exposes **Settings -> Connections -> SSH**.
3. Create a dedicated desktop-to-host key if it does not already exist. This
   key is used by unattended ChatGPT SSH connections, so create it without a
   passphrase and rely on the Windows account ACL plus the host-side Tailscale
   and SSH restrictions:

   ```powershell
   ssh-keygen -t ed25519 -N "" -f C:\Users\danie\.ssh\id_ed25519_forge_dev -C forge-dev
   ```

   Before rotating an existing key, move both halves to explicit backup names;
   never overwrite or delete the old private key until the replacement is
   verified. Confirm the new private key grants access only to the Windows
   account, `SYSTEM`, and local administrators.

4. Store only the `.pub` value in the HCP Terraform variable
   `desktop_ssh_public_key`. The private key remains on the desktop.
   Because the public key is rendered into cloud-init and
   `user_data_replace_on_change` is enabled, rotating it replaces the EC2
   instance while retaining the protected project volume. Store a fresh
   one-use Tailscale enrollment key before planning the replacement.
5. Deploy through the protected GitHub workflow; do not run Terraform locally.

## 2. Verify Tailscale and SSH

Confirm `forge-dev-01` is online with the approved tag. Use its exact full
MagicDNS name if the short hostname does not resolve. Tailscale may add a
numeric suffix while an older node with the same name remains registered.

Add a concrete entry to `C:\Users\danie\.ssh\config`:

```sshconfig
Host forge-dev
    HostName forge-dev-01-3.tail8c3304.ts.net
    User forge
    IdentityFile C:/Users/danie/.ssh/id_ed25519_forge_dev
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

The `HostName` above is the value verified on 2026-09-06. Replace it with the
current node's full MagicDNS name after an instance replacement.

Verify the host key out of band on first connection, then run:

```powershell
ssh forge-dev
```

The session must open as `forge`. Password and root login must fail. The host's
public IPv4 address is not an SSH endpoint.

## 3. Give the host repository-specific GitHub access

From an SSM session, switch to a `forge` login shell and create a key that is
separate from the desktop key:

```sh
sudo -iu forge
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_gptclaw -C 'GptClaw forge-dev-01'
```

Verify GitHub's published SSH host fingerprint before writing `known_hosts`.
Add only the public half as a write-enabled deploy key on
`danielbardsley/gptclaw`, titled `GptClaw forge-dev-01`. Configure a
repository-specific SSH alias with `IdentitiesOnly yes`, then clone into:

```text
/srv/forge/projects/gptclaw
```

Never copy the Windows GitHub deploy key onto EC2.

## 4. Authenticate Codex

As `forge`, first confirm the login shell can find Codex:

```sh
sh -lc 'command -v codex && codex --version'
```

Enable device-code login in ChatGPT security or workspace settings, then run:

```sh
codex login --device-auth
codex login status
```

If device-code login is unavailable, use the official localhost callback
fallback from the desktop:

```powershell
ssh -L 1455:localhost:1455 forge-dev
```

Run `codex login` in that SSH session and open the displayed address on the
desktop. Copying `auth.json` is not the normal fallback. If Codex uses file-based
credential storage, keep `~/.codex` mode `0700` and credential files mode
`0600`.

## 5. Add the remote project in ChatGPT

1. Open **Settings -> Connections -> SSH**.
2. Add or enable the discovered `forge-dev` alias.
3. Select `/srv/forge/projects/gptclaw` as the project folder.
4. Start a remote task and create `connection-test.md` containing the hostname
   and current UTC timestamp.
5. Run `hostname` and `date -u`, review the Git diff, remove the file, and
   confirm the repository is clean.

The desktop app starts and manages the remote Codex app server through SSH. Do
not expose an app-server listener on a public or shared network.
