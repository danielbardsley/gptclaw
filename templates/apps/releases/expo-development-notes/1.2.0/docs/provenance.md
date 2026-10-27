# Starter provenance

The native notebook screens, API adapter, local solid-color PNG and project guidance were
authored for GptClaw; no upstream demo scaffold or agent/plugin configuration is
vendored. This private starter declares UNLICENSED rather than granting a product
license. The package lock records exact public-package integrity. Expo 57.0.28's
published bundledNativeModules matrix and expo-template-default 57.0.30 package
metadata informed compatibility; their upstream source was inspected without
executing a generator. Framework/package assets are retained through their packages
with the upstream notices/licenses. The Node/pnpm installer is the existing reviewed
GptClaw toolchain recipe. App identities are documented fixed substitutions.

This successor removes the predecessor's temporary advisory exceptions. Its
frozen graph uses node-forge 1.4.1 and replaces the CLI's Zod 3 dependency with
Zod 4.6.7 through exact reviewed overrides; direct SDK/native pins are unchanged.
Both platform exports and the SDK check are required compatibility gates. The
single exact node-forge package-age exclusion covers its first 1,440 minutes
following publication on 2026-10-27T04:44:07.718Z; omit it in the next successor
after that window. No advisory severity is suppressed. Unexpected high/critical
findings still block verification. Native release/device acceptance stays separate.
