# Historical validator fixture

Unmodified project_manifest.py from GptClaw commit cce647680dfe63d3dafb8fcd51dad9fc132147e9.
It supports manifest versions 1–6. test_mobile_backend.py pins its SHA-256 and executes
it with the unchanged historical schema location to prove refusal of versions 8/9.
A committed fixture keeps this regression offline and independent of local branch
names or shallow CI checkout history. This is test source, not an installed provider.
