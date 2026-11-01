---
name: gptclaw-journey-verification
description: Demonstrate an approved application journey through its real interface, verify the resulting state and diagnose observed blockers. Use for end-to-end delivery and journey checks, not broad speculative hardening.
---

Read the approved user outcome, local guidance and actual runnable interface.
Choose the smallest principal journey that delivers that outcome. Set a bounded
first demonstration milestone and name the required gates. For UI applications,
exercise real UI through service/storage boundaries and reopen the result when
persistent state is promised. For API/CLI or stateless applications verify their
actual observable outcome without inventing a UI or storage requirement.

Demonstrate the normal journey early. Use the approved visual reference when one
exists and compare actual rendered output; reference renders are not application
screenshots. Follow [the journey record](assets/journey.md) proportionately.
A missing runtime is an actionable prerequisite; source checks can proceed but
cannot close the demonstration milestone. Preserve existing data and scope.

Fix the first observed blocker, add a focused regression where meaningful and
repeat the affected journey. Then exercise required interruption/retry/restart
cases. Preserve operation identity on uncertain replies and verify stored results,
not just success messages. Label synthetic inputs, doubles and device conditions.

Choose each next task by how directly it enables or proves the principal journey.
Defer speculative edge cases, broad refactors and optional polish with a reason
and revisit trigger. Successive hardening increments without journey progress
require explicit reprioritization. Address observed blockers, security/privacy/
data-loss risks and required acceptance gates as they arise; this ordering waives
none of them. A demonstrated core journey and full product acceptance are separate.
Report exact source/artifact/installed identity and evidence freshness. Never
claim native behavior from API probes, mocks, exports or component tests.
