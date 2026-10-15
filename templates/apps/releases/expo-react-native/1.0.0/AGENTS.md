# Native project guidance

Read the project specification, design and tasks before feature implementation.
This starter uses React Native, Expo Router and TypeScript; source lives in src/.
Use the exact declared rootless Node/pnpm toolchain and frozen dependencies. Follow
[mobile standards](docs/mobile-standards.md) and [architecture](docs/architecture.md).
Run platform format/lint/typecheck/test/build/security/verify commands, reporting
actual outcomes. build emits JavaScript/assets, not a signed binary. Preserve
unrelated edits and keep app changes on branches/PRs. Never put server/signing/API
secrets in source or client config. No host package installs, public Metro tunnel,
cloud build, store publication or native prebuild is authorized by this template.
