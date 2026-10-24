# Dashboard CPU investigation — October 24, 2026

The project owner requested diagnosis and correction of dashboard CPU use, including
associated collectors, with minimal background resource use.

A 20-second `systemctl --user show -p CPUUsageNSec` delta measured the installed
collector at 54.7% of one CPU core, the controller at 39.7%, and the frontend at 0.0%.
Their cumulative reader CPU was 61.6 and 47.2 hours over approximately 69 hours of
service lifetime. Percentages here are per core, not whole-host utilization.

The services continuously rediscovered projects and ran native ownership/readiness
and capability checks without viewers. Control rounds rested only two seconds.
Profiling also showed repeated trusted schema meta-validation: the forkserver
preloaded nine schema versions into a five-entry cache, evicting earlier versions.
This is separate from legitimate application workloads visible in process inspection.
The controller also reread every terminal operation record each second. Status rounds
that exceeded their interval ran continuously with virtually no rest.

The correction adds a shared 15-second viewer lease per service, pauses hidden-tab
polling, increases capability-round rest to five seconds, and expands the exact-byte
schema cache to 16 bounded entries. Current main supports more schemas than the
installed provider; the cache regression covers every bundled schema. Background
scans resume asynchronously after a snapshot read. Cached timestamps continue aging;
no expired status becomes current simply because a viewer returned. Operation
monitoring and fresh intent/submission validation remain active. Terminal records are
read for snapshots and retention checks; only unfinished/unknown operation IDs stay
in the background monitor. Each status round now rests five seconds after completion,
including slow/timeout rounds. Trusted catalogue validation and identical health probes
are coalesced within one isolated observation, with no reuse across refreshes.

Verification and installed-release results will be recorded below. Existing dashboard
release and provider snapshots are retained for rollback through the reviewed manager;
its active/unknown-operation and paused-runtime gates remain applicable. No application
runtime or persistent data needs replacement for this correction.

## Verification

- Deployed-source focused tests: `test_dashboard_collector.py` (10 tests),
  `test_dashboard_controls.py` (17), `test_dashboard_observation.py` (13), and
  `test_project_manifest.py` (29) passed. Tests cover idle/resume, shared leases,
  operation monitoring, full-schema cache reuse, exact-byte invalidation, one-read
  deduplication and enforced rest after a slow round.
- Current-main isolated worktree: `python -B -m unittest discover -s scripts/tests
  -p 'test_dashboard_*py'` passed all 92 tests before the final scheduling adjustment;
  the collector suite was rerun after that adjustment. All 29 manifest tests passed
  against its twelve bundled schemas.
- `scripts/tests/check_dashboard.py --engine podman` with existing pinned Node and
  browser images passed frozen dependency install, all 24 frontend tests, typecheck,
  production build, real Unix/HTTP boundaries, QR decode and browser acceptance,
  including hidden-tab pause and immediate visibility resume. Generated evidence is
  ignored under `.dashboard-qa/cpu-demand/`.
- `git diff --check`, staged diff checks and new relative documentation links passed.
- The broad prepared-environment `scripts/check-repository.sh` run is recorded below
  when complete. Terraform checks do not apply to this application tooling change.

## Private installation

Installed release: `7d73fb0e0594662345ec0b6d0a033f2fb70d5aa4d2e6d6ed774a9d82e4934c27`.
The reviewed manager prepared/activated each immutable release after disabling
submissions and checking owned units, active/unknown operations and paused runtimes.
The existing owned provider installer updated the stable launcher and loopback ingress
to satisfy the exact-provider controls compatibility gate. No project action was
submitted. Existing private handlers, source/data and earlier releases were retained.

The installed patch uses the existing dashboard/dark-mode source branch; the focused
PR targets current main separately and preserves its newer schema/runtime support.
No unrelated dark-mode work is included in the CPU-fix PR. No merge or owner browser
acceptance is inferred from these tests. Existing browser tabs need one reload to
receive the hidden-tab behavior.
