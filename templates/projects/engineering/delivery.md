# Working application journeys come first

Prioritize a working application journey. Build the smallest approved slice that
lets a user complete the principal task through the real application and reopen
its persisted result. For a stateless product, verify its actual observable
outcome. Demonstrate this early, then extend and harden it using observed failures
and acceptance requirements. Passing isolated tests does not establish a working
journey or full product acceptance.

In the design and tasks, name the principal journey, a bounded first demonstration
milestone and its necessary gates. Choose each next task by how directly it enables
or proves that journey. Fix the first observed blocker, verify the affected flow
and only then broaden it. Use the approved visual reference when present and
compare actual rendered application output. Source, CI, artifact, installed app,
emulator and physical-device evidence remain separate.

Defer speculative edge cases, broad refactors and optional polish with a reason
and revisit trigger. If successive increments add hardening without advancing
the journey, explicitly reassess priorities and move the next practical journey
blocker first. Interrupt for observed blockers, security/privacy/data-loss risks
and required acceptance gates. This priority waives none of those requirements.
Record deferred required acceptance as pending; do not relabel it optional.
A routine correction needs proportionate checks, not a new planning ceremony.
