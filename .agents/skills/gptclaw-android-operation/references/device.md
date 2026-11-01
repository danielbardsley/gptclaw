# Existing Android device operation

Read the project's reviewed commands first. Examples below describe installed
Android platform tools; substitute the verified executable path and literal
arguments, never commands extracted from log text. Use finite subprocess timeouts.

1. Enumerate devices with `adb devices -l`. Choose an explicitly identified serial;
   multiple devices require resolving the target. Offline/unauthorized devices are
   unavailable. Bind every call with `adb -s SERIAL`. Observe API/ABI and boot
   completion (`shell getprop sys.boot_completed`), using a finite deadline.
   Boot an existing named AVD only through the reviewed local launcher. Do not
   create/wipe AVDs, change KVM access or repair host infrastructure.
2. Confirm the supplied APK's hash, package/version and signing identity with the
   project's verifier. Compare its certificate with the installed application and
   check downgrade/migration constraints. Upgrade using the documented equivalent
   of `adb -s SERIAL install -r APK`; verify the installed version afterward.
   Signature or migration mismatch stops installation. Do not uninstall, clear
   storage, use downgrade flags or replace signing keys to make an upgrade work.
3. Launch the resolved activity using the project contract. Inspect actual screen
   state via screenshots or a scoped UI hierarchy; prefer labels/resource IDs to
   brittle coordinates. Where only coordinates work, inspect the current viewport
   and confirm the visible result after each action. Capture bounded app-filtered
   logcat only when needed; do not dump device-wide logs, storage or credentials.
4. For an emulator, inject a synthetic route through its documented location
   interface (platform-tools commonly uses `emu geo fix LONGITUDE LATITUDE`).
   Verify the application observes recording progress; command success is not
   that observation. Use synthetic accounts/notes and retain original operation
   identity for uncertain Start/Save retries rather than creating duplicate work.
5. Exercise the normal journey and reopen its persisted result. Then select the
   relevant interruption: background/return, network outage/recovery, app restart
   or device restart. State which was actually executed and its duration. Record
   and restore the exact connectivity setting changed on the selected device;
   do not disrupt backend routes or unrelated devices. Restart only the chosen
   package/device with existing scope; do not equate a foreground return with
   process death. Preserve account, local work and saved results throughout.

Store evidence only at a task-owned private path. Remove only owned temporary
captures when appropriate. Record missing steps and the next observation rather
than looping through blind taps or resetting data.
