# Reviewed Fieldnotes EAS tool inputs

These public npm manifests preserve the exact EAS 25.3.0 graph used for the
October 22 private Android trial. They contain no authentication or signing
material. The lock SHA-256 is
`08e4b5b107da32b518212323717acf2e28be24e456a53b8ca95d65281a76dec7`.

Copy these two manifests to a new task-owned user/container workspace and use
`npm ci --ignore-scripts --no-audit --no-fund` with the reviewed exact Node
24.21.0 toolchain. Never install host packages or store an Expo session in this
repository. Credential access and external jobs remain separately scoped.

The compatible transitive patches and owner-approved, expiring exception are in
[the build-tool review](../build-tool-review.md). Re-audit changed graphs; this
lock is not standing approval for other projects, iOS, stores, production,
paid builds or use after the October 28 expiry. Do not run npm audit fix to
silently replace reviewed inputs. Source/bundle verification, cloud compilation
and physical installation remain distinct evidence.
