# SPEC-050 acceptance evidence

Owner: project owner. Date: October 26, 2026.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md).

## Scope and revisions

Planning starter 1.1.0 adds engineering bundle 1.0.0 and the complete specification
skill with local links and source/hash provenance. Application creation adds the
same guidance plus a local planning index/catalogue, extending existing indexes.
Published application release assets and descriptors are unchanged. No existing
project (including Dogstats), installed provider, host policy or infrastructure
was modified. The standards preserve the existing reviewed rules; Markdown table
spacing was normalized to the mobile starter's formatter.

Implementation source is reviewed in [PR #107](https://github.com/danielbardsley/gptclaw/pull/107),
head `ad7974f` before this evidence update. The original source worktree retains
its separate dashboard history; the PR uses an isolated worktree based on
`89094b9`. Project-creation code/resources match between those worktrees; unrelated
dashboard commits are excluded from the PR.

## Criterion mapping

| Criterion | Evidence / state |
|---|---|
| PSI-AC01 | Local pass: 30 bootstrap tests, including local standard/skill hashes, missing inventory, complete output and unchanged retry. Actual candidate CLI preview/create/retry also passed. |
| PSI-AC02 | Local pass: all 11 provider families inherit standards, skill, planning context, valid local links and release provenance. Final focused creation/parity/reproducibility cases and mobile identity/inventory case passed after Markdown normalization. |
| PSI-AC03 | Local focused pass: missing/unmapped/symlink guidance, no-clobber collision, provider parity, release immutability and omitted committed starter-file regressions passed. The diagnostic repository run completed with the one corrected old inventory assertion; CI metadata/template checks pass but dependency-security cells fail as detailed below. |

## Executed local checks

- `.venv-manifest/bin/python scripts/tests/test_project_bootstrap.py`: **30 passed**,
  including a final run after Markdown normalization (**17.511s**).
- Template suite: **28 passed** (**167.645s**) before final formatting/release-gate
  additions. Final focused all-family inheritance, provider parity and
  reproducibility cases: **3 passed** (**142.314s**). The all-family case covers
  all **11** catalogue providers and checks generated hashes and local links.
- Corrected mobile exact inventory/identity regression: **1 passed**; final
  post-formatting run **25.949s**, including every additional file and its hash.
- Final complete-release inventory and historical immutability cases: **2 passed**
  (**62.359s**), including a staged synthetic standard omitted from its manifest.
- Missing guidance/inventory/collision cases: **3 passed**; final provider inventory/
  packaging/parity cases: **3 passed** (**50.675s**).
- Repository guidance: **10 passed**; specification skill: **10 passed**;
  workflow skills: **9 passed**. Skill/workflow suites passed again after formatting.
- Actual Prettier **3.9.10** checks passed for all **four** generated mobile
  families, each run from its own root with its actual config/ignore rules in a
  network-disabled GptClaw Node container. Legacy Expo **1.0.1** also passed
  after repository-guidance adaptation, retaining the local standards link and
  specification skill. No ignore rule or quality gate was weakened. Both owned
  formatter/generated-app fixtures were removed after evidence collection.
- Candidate CLI at `606f272`: preview made no destination writes; creation
  recorded **14** starter-file hashes; unchanged retry passed. Only a task-owned
  synthetic fixture was created and removed.
- Release integrity/immutability and **285** changed-document relative links
  passed at the earlier checked source revision. Final PR-scoped review passed
  **296** real relative file links outside literal code examples; tracked/staged
  whitespace checks and final release completeness/immutability checks passed.
  Heading-anchor semantics and external URLs are outside this file-target review.

The broad `PATH="$PWD/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh`
run started while implementation was evolving. It encountered the old mobile
inventory assertion, which expected the pre-extension file list. That assertion
was corrected without excluding new files; its focused reruns pass. The template
reproducibility assertion was similarly updated for documented project-title
substitutions while still checking every generated hash. Source kept changing
between independent suites, so this broad run is diagnostic evidence, not a claim
of final-head whole-repository acceptance. It completed **52 reported suites /
1,000 tests**, exit **1**, with only that old inventory assertion failing and no
reported skips. All remaining diagnostic suites passed. The corrected inventory
case passed independently, including its final post-formatting rerun. The entire
checker was not rerun on a frozen final head; this limitation is retained rather
than describing the diagnostic command as successful.

## CI and retained limitations

[Quality matrix run 40419884267](https://github.com/danielbardsley/gptclaw/actions/runs/40419884267)
at `ad7974f`: metadata passed (including generation, negative cases and the complete
release-inventory gate); Fastify's full generated cell passed. All ten other
failed cells were inspected and fail in dependency-security checks against
unchanged release locks/advisory policies: Python reports locked-package audit
findings; Next.js/static/notes report audit findings; all four Expo families fail
on unaccepted high/critical advisories or expired exceptions. No dependency update,
audit suppression or exception renewal is part of this change.

The Expo React Native and development cells passed lint/formatting, types, tests
and source build before their security failure. This confirms the copied-file
formatting defect found in an earlier CI run is fixed; it does not establish full
matrix success, signed native/device acceptance or production readiness.
At the same code commit, the private application workflow's
[template job](https://github.com/danielbardsley/gptclaw/actions/runs/40419884281/job/121911377051)
and TypeScript API job passed. Five other integration jobs show dependency-audit
failures; the legacy mobile-source job exposes only an opaque generated-workflow
failure and a runner-local child-log path. Its exact child error was unavailable;
local legacy formatter/reference verification passed, and the current Expo matrix
cells explicitly identify security-audit failures. Terraform workflow checks are
still running. No green aggregate CI or final documentation-head CI is claimed.

Merge, installed-provider rollout and fresh-client guidance discovery remain
separate. Bootstrap requires a reviewed commit with the new inventory. Copying
standards cannot prove instruction loading or that a future product implemented
all its gates. Existing projects require separate adoption, explicitly excluded
here. No local Terraform, production operation or installed-device check ran.
