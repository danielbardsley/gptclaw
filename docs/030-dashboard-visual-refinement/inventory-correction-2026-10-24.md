# Dashboard inventory and overview correction — October 24

The project owner requested removal of the Docs column and correction of the
partial inventory warnings. Documentation presence remains available in expanded
project details; the table span now matches the overview column count.

## Cause and correction

The installed collector used a provider from before schema 10 support. Two valid
static projects consequently produced `version` diagnostics and were omitted from
the inventory. Current main already contains their complete validator/runtime
support. The private dashboard was rebuilt against that provider, retaining the
installed theme and the CPU fixes from PR #105. No diagnostic was suppressed and
no project manifest or runtime data was modified. Static inventory regression
coverage now verifies two schema-10 projects without starting any runtime.

The immutable private release is
`bdb7ac612f81e2a9728089bae1c4cd1935cc5830d3e753f23725d5c2c9140c3f`.
The previous release is retained by the manager. Submissions were disabled, idle
operations verified, and the existing ownership-checking `ensure_ingress` installer
aligned the stable provider/private router before manager activation. No project
start/stop/restart, migration, Serve change or infrastructure apply was performed.
The existing dark-theme work remains on its separate deployment branch; the
main-based review branch contains the requested column correction and regression
coverage.

## Verification

- Focused dashboard verification: all 10 suites / 109 tests passed
  with exit 0, including 14 inventory tests and complete two-static-project coverage.
- Frontend: 24 tests, typecheck and production build passed with the existing pinned
  Node/pnpm container.
- Container browser assertions passed for overview columns/full-width details,
  responsive bounds, theme, controls, stale/partial/failure/recovery behavior,
  private HTTP/socket boundaries and QR rendering. The harness printed its final
  pass marker but the enclosing command returned signal exit 143; this is not
  recorded as a clean whole-harness exit.
- The broad repository checker was attempted: 17 completed suites / 322 tests
  passed before termination (143) during the mobile-project suite. No preceding
  failure marker was recorded. This does not establish a complete repository pass.
- A separate actual HTTPS Chromium smoke check exited 0: six project rows,
  `Inventory current`, no diagnostics, no Docs column, correct expanded-row span,
  retained README/index details and working theme toggle. All three dashboard
  services are active. After initial collection, all six project statuses were
  current; one transient database health reading recovered on the next round.

Local logs/captures remain task-owned, outside commits. PR CI and project-owner
acceptance remain separate from this local/private verification.
