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
- `PATH="$PWD/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh` completed
  with exit 0 on the deployed-source branch (46 unittest suites / 895 tests,
  plus the script's other invariants and fixture checks). Terraform checks do not
  apply to this application tooling change.

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

## Final measurements

With the exact owned frontend temporarily stopped, no active/unknown operations,
a 30-second drain and a subsequent 20-second service-accounting sample, idle CPU was
0.022% of one core for the collector and 0.017% for the controller (0.039% combined).
The frontend was restored in a `finally` block and all three services were active.
This controlled interval excludes ongoing browser requests; it does not claim an
actively viewed dashboard is idle.

A subsequent 30-second sample with five-second snapshot polling measured 36.87%
collector CPU, 2.85% controller CPU and 1.722% frontend CPU. All four inventoried
projects had current status, and inventory was current after resume. Viewed collection
still performs ownership/readiness validation and native probes; it uses more CPU
than the sleeping services. These measurements are workload-specific, not universal
resource limits. Existing browser clients continued polling during earlier uncontrolled
idle attempts, so those intervals were not used as idle acceptance evidence.

[Focused PR #105](https://github.com/danielbardsley/gptclaw/pull/105) targets main;
review/CI/merge remain separate from the installed private fix.

Dashboard CI passed on implementation commit `93905f1`:
[Private platform dashboard run](https://github.com/danielbardsley/gptclaw/actions/runs/40108292650).
Other workflow runs and final documentation-head CI remain pending; no infrastructure
plan/apply or production deployment was performed. Both source worktrees are retained,
and task changes are committed rather than discarding earlier work.

## Active-view follow-up — October 24

The project owner rejected the approximately 40% viewed CPU result and requested a
substantial further reduction with useful status. The follow-up removes repeated
full catalogue validation, per-resource CLI startup, HTTP TLS initialization and
per-poll PostgreSQL client startup. Worker startup also re-executed the collector
module, defeating parts of preloading; new provider snapshots use a thin launcher.

Trusted semantic validation is reused only after all contributing bytes and safe
file/directory properties match; it never caches project health or bypasses mutable
project validation. Native batches contain only exact inventory-derived targets and
fixed projected fields. Workers continue ownership/image/port/unit checks; old or
unknown native data falls back to independent reads. Database read sessions are bounded
to eight, use only a fixed revision SELECT and are replaced on container/credential
changes, failed queries, idle expiry and shutdown. Extra DBs retain one-shot queries.

The resource profile rests 15 seconds between completed status/capability rounds,
retains the 30-second stale threshold, and targets observed transitions within
30 seconds under supported load. Browser requests still read shared caches every
five seconds, and lifecycle actions still validate immediately. This intentionally
replaces the original 15-second transition target under the owner's resource priority.

Final verification and private installation results are recorded below when complete.

### Active-profile verification and installation

The deployed-source dashboard suite passed all **108 tests**. The main-based PR
passed its complete 107-test suite before the final per-project client-start failure
hardening; the final 13-test reader suite then passed on that tree. Tests cover exact
byte changes with restored timestamps, symlinks/hardlinks, copy isolation, scoped and
expired native reads, fixed SQL, persistent reuse, eight-session capacity and one-shot
fallback, instance/credential changes, timeout/reaping, shutdown, and sanitized errors.

The container harness passed all 24 frontend tests, typecheck, production build,
Unix/HTTP boundaries, local QR decode and browser acceptance using the new thin
launcher. Release/rollback-entrypoint tests passed (12), private-app tests passed (36),
changed shell syntax and diff/link checks passed. Full repository results follow below.
No new project action, migration, database mutation, public exposure, host package or
infrastructure change was used for acceptance.

A bounded task-owned private systemd fixture measured 6.665% collector CPU during a
60-second viewed sample, with all four projects current and a maximum sampled age of
16.413 seconds. Idle collector CPU was 0.027% after the lease drained. The fixture and
its PostgreSQL readers were stopped and its temporary socket namespace removed.

Private installed release:
`36f1e10a2f16a0c9b51ff777cdb510a67a6977483541bde1d12a8ce564cc9f6d`.
Activation used the reviewed manager, idle-operation/paused-runtime checks and the
owned provider installer. The preceding release is retained. Existing dark-mode UI,
project processes, persistent data and private handlers were preserved.

After a 30-second warmup, a 60-second installed-stack sample with five-second browser
snapshot polling measured percentages of one CPU core as follows:

| Service | Before active-profile fix | After |
| --- | ---: | ---: |
| Collector | 36.870% | 8.546% |
| Controller | 2.850% | 1.085% |
| Frontend | 1.722% | 0.351% |
| **Total measured dashboard services** | **41.442%** | **9.982%** |

The readers alone fell from 39.720% to 9.631% (approximately 76% less CPU).
All four projects were current in every sample; maximum sampled status age was
18.265 seconds. These are observed workload-specific results, not universal caps.
Installed-service measurements are authoritative; the private fixture uses a different
source/provider path and does not stand in for the complete installed stack.
The observed memory was approximately 144 MiB collector, 38 MiB controller and
107 MiB frontend. All three services were active and the listener remained loopback.

The final prepared-environment `scripts/check-repository.sh` run exited 0:
47 unittest suites / 910 tests plus the other repository invariants passed. The
complete check includes the newly registered reader tests; the final private-app
packaging test was also run separately after introducing the thin launcher.
Review/CI/merge for the updated PR remain separate from private installation.
