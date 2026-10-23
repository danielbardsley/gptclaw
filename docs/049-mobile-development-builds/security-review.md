# Native build security disposition — October 23, 2026

Status: External native builds blocked by the implemented audit gate.
Owner: Project owner. Related: [specification](spec.md), [runbook](../../runbooks/manage-development-builds.md).

A credential-free container built the complete integrity-locked `eas-cli@25.3.0`
toolchain with install scripts disabled. `npm audit --json` in that container
reported 0 critical, 9 high, 11 moderate and 1 low vulnerable package entries.
This was a local tooling audit, not an EAS build or a signing acceptance check.
No Expo account, token, signing key, billing setting or cloud job was accessed.

| Package | Severity | Upstream advisory / source | Disposition |
|---|---|---|---|
| @expo/code-signing-certificates | high | Transitive dependency chain | Tool reports a fix; review exact compatibility before changing pins |
| @expo/pkcs12 | high | Transitive dependency chain | Tool reports a fix; review exact compatibility before changing pins |
| eas-cli | high | Transitive dependency chain | Tool reports a fix; review exact compatibility before changing pins |
| jks-js | high | Transitive dependency chain | Tool reports a fix; review exact compatibility before changing pins |
| joi | high | https://github.com/advisories/GHSA-6h2x-m376-mqjq, https://github.com/advisories/GHSA-6w3j-5fw6-r9vr, https://github.com/advisories/GHSA-gg4h-3hg2-grpc, https://github.com/advisories/GHSA-q7cg-457f-vx79, https://github.com/advisories/GHSA-wr44-6hxh-3jwq | Tool reports a fix; review exact compatibility before changing pins |
| minimatch | high | https://github.com/advisories/GHSA-23c5-xmqv-rm74, https://github.com/advisories/GHSA-3ppc-4f35-3m26, https://github.com/advisories/GHSA-7r86-cg39-jmmj | Tool reports a fix; review exact compatibility before changing pins |
| nanoid | high | https://github.com/advisories/GHSA-28wg-ghj8-5hjv, https://github.com/advisories/GHSA-2v37-7h3g-55p8, https://github.com/advisories/GHSA-xwg4-73v4-xw9w | Tool reports a fix; review exact compatibility before changing pins |
| node-forge | high | https://github.com/advisories/GHSA-86w9-cpqp-85rv | Tool reports a fix; review exact compatibility before changing pins |
| tar | high | https://github.com/advisories/GHSA-r292-9mhp-454m | Tool reports a fix; review exact compatibility before changing pins |

These findings include archive and signing libraries. The previous Go/source-only
exceptions were deliberately not imported into the native submission gate. The
new gate audits source dependencies and the EAS tool image without credentials
and rejects any high or critical count before uploading or submitting a job.
Source-only exports passing their existing policy cannot certify signing.

Next action: implementer reviews upstream supported fixes and exact transitive
compatibility; project owner reviews any unresolved finding against a concrete
native-build scope. A future exception, if selected, needs exact findings/versions,
owner, scope, rationale, expiry and removal step, plus a reviewed gate change.
There is no exception or bypass authorized here. API/private transport and
physical-device acceptance remain separate gates. The named SDK-57 compiler image
and CLI version have source/registry evidence; a successful native cloud build
has not established their full compatibility.

## Native source dependency audit

The new immutable source lock was separately checked with `pnpm audit --json`
in the reviewed Node container: 0 critical, 2 high, 2 moderate, 0 low. The high
findings are node-forge 1.4.0 (`GHSA-86w9-cpqp-85rv`) and transitive Zod
3.25.76 (`GHSA-mrhx-c7xc-m3w5`, through the pinned Expo CLI). The source-only
security gate rejects the unapproved Zod finding. The upstream advisory was
updated October 23 and names 4.6.6 as patched; the registry's last stable Zod 3
release is 3.25.76. Forcing the Expo CLI from Zod 3 to 4 is a major compatibility
change, not an established safe patch. No new exception was added. Native
submission/runtime require zero high/critical findings independently of source
exports; both remain blocked.

[Zod advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5). Unsigned
exports are checked offline without credentials, independently of this failed
security gate; they do not establish signing or native runtime admission.

## Automatic remediation review

For every high package chain, npm's `fixAvailable` suggestion selects EAS CLI
0.24.1 as a semver-major change from 25.3.0. That is a major historical downgrade,
not a verified SDK-57-compatible repair, and was not applied. Source Zod's listed
patched release is a different major from Expo CLI's pinned transitive selection.
No safe complete automatic remediation has been established for these pins; a
reviewed tooling change or exact scoped risk decision is still needed. No broad
`audit fix --force`, dependency-policy relaxation or advisory exception was used.


## Broader CI audit boundaries

The generated matrix also found fresh advisories in existing immutable Next and
Python starter releases (including Next critical/high entries and Python
filelock/virtualenv entries). Those releases were not edited or silently waived.
Fastify source checks passed. These broader CI failures remain separate from the
new native source and EAS admission findings above; passing component tests does
not imply a passing dependency audit or approval to sign/upload source.


## Rechecked after account authorization — October 23

Credential-free public npm metadata still names EAS 25.3.0 and node-forge 1.4.0 as
latest. EAS pins node-forge 1.4.0 directly; latest certificate/PKCS12/JKS wrappers
also depend on node-forge ^1.4.0. The [node-forge advisory](https://github.com/advisories/GHSA-86w9-cpqp-85rv)
still lists no patched version. Zod latest is 4.6.7, but latest Expo CLI 58.1.15
still requires Zod ^3.25.76 and node-forge ^1.4.0. An SDK migration or forced
major override is not an established repair. These are registry/advisory checks,
not fresh installation/audit/test evidence. Frozen source and gates are unchanged.

Next technical step is a supported upstream repair or a separately reviewed,
tested minimal dependency patch. A security exception would require a concrete
call-path/exposure assessment and the existing explicit disposition fields; the
owner's account/build/payment choices do not authorize an exception.
