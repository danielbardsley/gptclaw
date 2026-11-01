# Required engineering standards

These references are copied at project creation, independently of application
release files. They remain available without the original GptClaw checkout.

| Applicability                  | Required reference                                      |
| ------------------------------ | ------------------------------------------------------- |
| Every implemented stack        | [Shared quality and TypeScript conventions](quality.md) |
| Python / FastAPI components    | [Python engineering standards](python-standards.md)     |
| Expo / React Native components | [Mobile engineering standards](mobile-standards.md)     |

Read the applicable rows before designing or implementing a component. Mixed
stacks use every applicable row. A planning-only project retains all references;
select applicability when its stack is chosen. For a new language, define and
review its local standards and gates before implementation rather than assuming
these references cover it. Preserve these files when removing starter demos.

Read [working journey priorities](delivery.md) before material planning and
implementation. The generated skill selection guide at `docs/engineering/skills.md` describes local
workflow availability and later capability selection.

## Standards become implementation gates

The technical design must map applicable requirements to actual formatter/lint,
type, test/coverage, security, build and CI commands, plus relevant accessibility,
contract, migration and dependency checks. Tasks must implement and verify those
gates. Keep commands consistent locally and in CI; do not silently omit coverage,
security or formatting checks because unit tests pass. Record each justified
adaptation or inapplicable requirement with rationale, owner and review status.
A changed formatter or line limit is an explicit adaptation, not silent inheritance.

The references describe established template contracts. Example routes and sample
fixtures are not product requirements. Managed prefixes apply only to projects
using that routing model. Paths and commands in quality.md describe an application
starter with quality.json/checks; use them only when those files actually exist.
For planning or custom stacks, implement equivalent gates with the selected
reviewed tools and document exact commands; do not claim tools are installed or
checks pass from these documents alone. Existing component guidance remains
applicable; resolve consequential conflicts in the project-owned design.

Record source hashes in the creation provenance. Future standards updates are
explicit reviewed project changes preserving adaptations, never background sync.
Copying references cannot prove that an agent loaded them or that checks ran.
