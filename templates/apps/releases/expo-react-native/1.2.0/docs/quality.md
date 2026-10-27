# Application quality

Run `python3 checks/gptclaw_quality.py inspect` without executing source.
Run `python3 checks/gptclaw_quality.py verify --engine podman` locally, or use
`--engine docker` on an isolated CI runner. Python 3 and the selected container
engine are the only host prerequisites. The quality contract is quality.json v1;
lifecycle manifests retain their existing versions and meaning.

The same entrypoint accepts format, lint, typecheck, test, build and security.
Format deliberately writes source; verify checks formatting without rewriting it.
Frozen restore uses the exact pinned container recipes and lockfiles. Security
advisory outages fail rather than pass. Mobile build emits JS/assets, not signed
binaries. Persistent tests use only the disposable database integration adapter;
no managed database or credentials are reused.

TypeScript/JavaScript: use the formatter, strict TypeScript and ESLint rules;
camelCase functions/variables, PascalCase components/types, descriptive names,
thin routes and separate domain/services. Keep errors typed and render user text
as text. Python retains docs/python-standards.md in the relevant component.

Dependency automation is weekly with one PR per ecosystem/directory and no
auto-merge. Major and coupled Expo/React Native/profile upgrades require an
explicit compatibility review. New updater PRs must preserve exact pins and
pass frozen restore and standard checks. An unavailable registry is a failure.
Pause by reviewing a config change; record owner, reason and review date for
deferrals. Private registries and new credentials are outside this setup.

Accessibility: automated web checks use the bundled exact axe artifact where a
browser adapter exists; native tests assert names/roles/state. Manually check
keyboard/focus, screen-reader navigation/errors, contrast, 200% zoom, narrow
layout, reduced motion and enlarged text before product acceptance. Android
TalkBack and iOS VoiceOver acceptance remain separate from source tests.

Contract, migration, performance, smoke and release-notes subcommands accept
explicit JSON evidence inputs (see --help and the platform quality runbook).
Performance comparison requires reviewed numeric budgets and matching profile
baselines; missing measurements never constitute a pass. Migration static
analysis is advisory: backup/restore and managed plan/apply gates remain required.
Release-note generation produces a local reviewed draft only, never tags or
publishes. Historical releases and existing applications are not auto-upgraded.
