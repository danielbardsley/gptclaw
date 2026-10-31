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
The owner subsequently requested automatic machine setup instead of the proposed
manual SSM repair. Do not run the earlier two commands; that recovery path has
been superseded. No successful manual repair has been observed.

### Recovery completed; exception retired

The project owner approved one pipeline replacement of the failed instance and
its own fresh root disk, followed by restoration of its lifecycle guards. The
[reviewed plan](https://github.com/danielbardsley/gptclaw/actions/runs/41218238098)
and [apply](https://github.com/danielbardsley/gptclaw/actions/runs/41223764115)
used revision `379fc9f` and state **running**. HCP apply:
[run-WBWyfSrF2cVmyEsc](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-WBWyfSrF2cVmyEsc).
The apply added/replaced only the Android instance/state resources, destroyed
the failed runner `i-00eecaeb4e941cf5e`, and updated 14 revision tags.
Replacement: `i-0128be3340461d289`.

The one-replacement exception is now expired. This follow-up restores
`prevent_destroy = true` and `ignore_changes = [ami, user_data_base64]` and removes
`create_before_destroy`; merge it before any subsequent infrastructure apply.
No further replacement or manual SSM repair is authorized by this record. Do not
rerun the earlier manual repair proposal. The existing host/project-volume
protections and IAM/networking were preserved.

Live private SSH as forge verified KVM read/write access, active Android service,
`sys.boot_completed=1`, loopback emulator/ADB listeners and the four-hour stop
timer. An actual launcher screenshot was captured locally. Fresh SSH host trust
was established on first use through the newly enrolled private tailnet node;
subsequent connections require that saved host key. Android app and physical
device acceptance are separate from these runner observations.

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

## Guidance inherited by projects

New planning and application projects receive the portable
[Android testing guide](../templates/projects/engineering/android-emulator.md)
through engineering bundle 1.1.0. Mobile standards link to it; it covers ordinary
project testing, not provisioning or recovery. Existing projects need an explicit
reviewed adoption. Allocate a shared-emulator slot and approved access per project;
the Dogstats private-key path above is not a credential source for other projects.
