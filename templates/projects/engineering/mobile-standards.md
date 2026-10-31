# Mobile engineering standards

Use strict TypeScript, named reusable components, idiomatic hooks and explicit
props. Keep screens in src/app and tests elsewhere. Prefer React Native components,
local assets, accessible labels/roles, 48-point touch targets and safe-area/keyboard
handling. Treat loading, error and reconnect behavior as real product requirements
when a backend is introduced. Test observable interactions and regressions, not
only snapshots. Run Prettier, ESLint and types before publishing; avoid hidden
native configuration, dynamic app config or unsupported config plugins. Dependency
changes use exact versions through reviewed staged operations; SDK/core package
changes require a new reviewed compatibility matrix. Never store confidential
values in EXPO_PUBLIC or any compiled client configuration. Remove unrelated demo
content and update tests/routes/docs together when adapting a product.

For Android interaction tests, read [the private emulator workflow](android-emulator.md).
Use project-approved access and fixtures; record emulator evidence separately
from physical-device and product acceptance.
