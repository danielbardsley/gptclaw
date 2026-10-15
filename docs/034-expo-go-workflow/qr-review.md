# Local QR dependency and artifact review

- **Owner:** Project owner
- **Observed:** October 14, 2026 UTC
- **Scope:** SPEC-034 local encoder and independent test decoder; no native certification
- **Specification:** [SPEC-034](spec.md) · **Acceptance:** [Evidence](acceptance.md)

| Package | Role | License | Runtime dependencies | Exact npm integrity |
|---|---|---|---|---|
| toqr 0.1.1 | Local pure QR encoder | MIT | None | sha512-FWAPzCIHZHnrE/5/w9MPk0kK25hSQSH2IKhYh9PyjS3SG/+IEMvlwIHbhz+oF7xl54I+ueZlVnMjyzdSwLmAwA== |
| jsqr 1.4.0 | Independent test-only decoder | Apache-2.0 | None | sha512-dxLob7q65Xg2DvstYkRpkYtmKm2sPJ9oFhrhmudT1dZvNFFTlroai3AWSpLey/w5vMcLBXRgOJsbXpdN9HzU/A== |

Exact metadata came from registry.npmjs.org, with fixed package/version/HTTPS URLs
and no redirects. The encoder's installed license/API/source and the decoder's
published metadata were inspected. The frontend package and lockfile pin both
versions; encoder integrity matches the delivered Expo lock graph. Existing package
versions are preserved. Install used the pinned Node 24.21.0 / pnpm 12.10.1 image,
with scripts/hooks disabled and no host package or account install. An initial
`pnpm add` rejected the install-only `--no-runtime` flag before mutation; installed
`add --help` was checked and supported add flags used. Frozen install subsequently
used the normal reviewed install guards. No version update notice was acted upon.

The complete fresh frontend audit returned zero advisories at every severity.
No Metro exception was added or widened. Licenses remain with package distribution;
the decoder is a development test dependency, not a native-app/client dependency.

Four QR cases pass within thirteen frontend tests: complete synthetic session URL
round-trip with an independent decoder; minimum/maximum payloads; malformed/oversized/
control/Unicode input rejection and no markup interpolation; deterministic quiet-zone/
no-network rendering. The portable pinned browser additionally rasterized the actual
320-pixel SVG and decoded its complete synthetic URL/nonce exactly. Browser traffic
for this QR check is offline. Frontend type checking and production build pass; the
full existing portable HTTP/socket/browser regression also passes.

No actual owner launch URI, account token, device identifier, external QR service or
web forwarding page enters these tests. Public Go payload generation, CLI artifact
ownership/expiry and minimum dashboard launch action remain unfinished. A scannable
synthetic SVG is not evidence of a loaded native client.
