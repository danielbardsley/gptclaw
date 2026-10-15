# React Native / Expo starter

This is a native iOS/Android source starter. Use the exact toolchain declared in
`.gptclaw/toolchain.json` through the reviewed GptClaw CLI. Creation itself installs
nothing. `deps install` prepares the frozen lockfile; `verify` checks format, lint,
types, native component behavior, SDK coherence, security and both native-target
JavaScript/asset bundles. `format` deliberately changes source.

`build` exports bundles into ignored `.gptclaw-build/`; it does not compile or sign
APK/IPA files. Managed Metro/device access, backend binding, EAS and production
release commands are not delivered by this starter. Development app IDs are public
synthetic identities, not registered store IDs. No runtime secrets or dotenv files
are accepted. Use the repository mobile standards and architecture notes.

The counter/about screens are deliberate synthetic examples for starter acceptance.
Replace them for a product unless its specification retains them. Keep reusable
accessibility, quality and platform contracts; inherited example tests alone do
not establish product acceptance. Do not regenerate or delete hand-edited native
source through this adapter.
