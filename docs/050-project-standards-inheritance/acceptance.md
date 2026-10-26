# SPEC-050 acceptance evidence

Owner: project owner. Date: October 26, 2026.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md).

Planning starter 1.1.0 adds engineering bundle 1.0.0 and the complete specification
skill with local links and source/hash provenance. Application creation adds the
same guidance plus local planning context as a separately recorded layer,
extending existing documentation indexes. Published application releases,
existing projects (including Dogstats), installed providers, host policy and
infrastructure remain unchanged.

| Criterion | Local evidence |
|---|---|
| PSI-AC01 | 30 bootstrap tests passed, including standards/skill hashes, missing inventory and unchanged retry. |
| PSI-AC02 | Focused all-family test passed for all 11 providers, checking local links and preserved release provenance. Final full template suite pending. |
| PSI-AC03 | Three focused missing-resource/inventory/collision tests passed. Full repository and final provider-parity results pending. |

Executed: bootstrap suite (30 passed), focused all-family test (passed), three
failure/collision cases (passed), repository guidance (10 passed), specification
skill (10 passed), workflow skills (9 passed). Diff whitespace and checker shell
syntax passed at the checked intermediate revision. Full offline checker and
final template suite remain in progress.

Initial tests exposed a wrong assumption about the fixture's Path return value;
that test was corrected. Missing-resource failures were normalized to the
existing template-policy error contract and their regression passed.

No Terraform, app build, CI, deployment or fresh-client discovery is claimed.
Installed providers retain their bundled revision until a reviewed update.
Bootstrap requires a reviewed source commit containing the new inventory.
Copied standards do not prove instruction loading or gate execution.
