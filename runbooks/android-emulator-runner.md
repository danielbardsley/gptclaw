# Private Android runner

[Scope/approval](../docs/051-android-emulator-runner/spec.md) ·
[Design](../docs/051-android-emulator-runner/technical-design.md)

One separate M7i instance runs Android; Dogstats remains on the existing host.
Only synthetic test data belongs on this appliance. No project volume, backend,
credentials or Tailscale state are copied.

## Provision and start/stop

After review/merge, open the [Terraform development host workflow](https://github.com/danielbardsley/gptclaw/actions/workflows/terraform-dev-host.yml).
Run on **main**, operation **plan**, Android runner state **running**. Inspect
the HCP plan: expected additions are `aws_instance.android_runner` and
`aws_ec2_instance_state.android_runner`, cloud-init/output changes and ordinary
revision tags. Reject unexpected existing-host replacement, project-volume
resize/detach/destruction, ingress or IAM expansion. Then dispatch **apply**,
state **running**, confirmation **gptclaw-dev-host**, with existing environment
approvals. Retain the revision and GitHub/HCP links. Never apply locally.

For later start/stop use that same plan/apply path with **running** or **stopped**.
Default dispatch state is **stopped**, including unrelated future applies. A
four-hour boot timer stops Android and shuts down the runner, allowing up to 90
seconds for graceful exit. The encrypted disk survives stop/start; storage and
applicable IPv4/network charges remain. The timer is not a hard billing cap.

## First-boot SSH runtime-directory failure

The October 31 apply created runner `i-00eecaeb4e941cf5e`, but cloud-init
stopped at `sshd -t` with `Missing privilege separation directory: /run/sshd`.
KVM existed; Tailscale had not been installed and Android had not started.
The bootstrap now explicitly creates the root-owned 0755 runtime directory
before validating SSH, including on images using socket activation.

Updating ignored cloud-init source does **not** repair an existing instance.
Do not remove lifecycle guards, replace its disk, broaden IAM or rerun Terraform
and claim recovery. The project owner **approved this two-command operator
exception** on October 31, 2026 because the pipeline-created runner failed before enrollment.
Owner: project owner. Scope: this failed first boot on the named instance only.
The exception expires after this one repair attempt; it grants no standing
permission. Remove the exception from active recovery instructions once the
attempt is recorded, retaining the historical evidence. It is not authorization
for the agent to use sudo or for general manual host changes.

Only on the named runner, after confirming that exact failure and that bootstrap
has finished, an authorized operator can use the existing SSM session:

```sh
sudo install -d -o root -g root -m 0755 /run/sshd
sudo /usr/local/sbin/gptclaw-android-bootstrap
```

This resumes the existing committed bootstrap, including its unchanged firewall,
artifact checksums, federation, unprivileged installer and stop timer. It does
not reset the failed cloud-init status or change the persisted bootstrap source;
cloud-init will continue to record the historical first-boot failure. Do not
run `cloud-init clean`, disable the firewall or clear any disk/app data. If the
script fails again, stop and diagnose the exact error rather than retrying
blindly. Share only non-secret status/error lines, never federation tokens.

After completion check Tailscale enrollment, Android boot and the stop timer as
below. No Android acceptance is inferred from this repair. If the repair fails,
retain the disk and prepare a separately reviewed recovery;
do not assume this exception authorizes another privileged repair.

## Connect and verify

Bootstrap downloads approximately 2.3 GB of pinned Android archives. Terraform
success does not establish bootstrap, tailnet enrollment or Android readiness.
Confirm the fresh `forge-android-01` node/tag and verified SSH host fingerprint.
If bootstrap fails, use reviewed SSM/operator diagnosis; never open public ingress
or grant forge sudo. The owner accepted Android SDK terms for this runner on
October 30, 2026; bootstrap records `/home/forge/android/license-accepted`.

From the development host, leave this tunnel running (use the actual tailnet DNS
name if the short hostname is not resolved):

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -i /srv/forge/projects/dogstats/.local/android/emulator-runner-access/id_ed25519 \
  -L 127.0.0.1:15555:127.0.0.1:5555 forge@forge-android-01
```

Connect using Dogstats' pinned `platform-tools/adb connect 127.0.0.1:15555`;
always select serial `127.0.0.1:15555` for subsequent commands. Check `sys.boot_completed`
equals **1**, inspect a launcher screenshot and exercise input. As forge on the
runner, verify `/dev/kvm` is readable/writable, `emulator -accel-check` succeeds,
`systemctl list-timers gptclaw-android-stop.timer` shows the stop timer, and `ss -ltn`
shows only loopback emulator/ADB listeners. Confirm any authorization prompt
belongs to this dedicated emulator; don't control an unrelated phone.

Install the inspected APK; verify version, actual app screens and Android access
to `forge-dev-01-4.tail8c3304.ts.net` API/issuer ports 8443/8444. Test synthetic
sign-in → walk → stops/notes → End → Save → History/reopen against the original
design. Don't capture credentials, inbox action links or real private locations.
Emulated GPS does not establish physical-device recording/battery acceptance.

Stop only this runner through Terraform when finished; close its SSH tunnel.
Preserve the disk on failure. Removal/replacement requires a reviewed change to
its destruction guard. The private key stays in ignored Dogstats local storage;
retiring the public key in source alone does not revoke an already provisioned
authorized_keys entry. Source rollback likewise does not roll back disk data.
