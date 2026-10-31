# Project guidance verification — ER-07 / AC-06

Owner: project owner. Date: October 31, 2026.
Source change: `4343333` on top of merged runner guard restoration `7b5fe51`.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md).

## Changed behavior

Engineering bundle 1.1.0 adds a portable Android emulator guide, linked from
mobile standards and the applicability index. Both planning bootstrap and
application creation copy/hash it; provider packaging includes the same bytes.
The bootstrap skill describes the inherited guide and access/session prerequisites.
Published app releases, existing project provenance and installed providers remain
unchanged. The canonical runner runbook links to the inherited guide.

Dogstats explicitly adopts a project-owned guide with its existing ignored
SDK/key paths, package, private endpoints and walk acceptance instructions.
Its root AGENTS and documentation index link to the guide. The publication uses
current main `bf3ff804`, preserving the separate application PR and original
checkout's uncommitted work. No key contents or runtime data were inspected.

## Local checks

Using the existing Python 3.12 manifest environment, from the isolated GptClaw
worktree:

- `python3 -m unittest discover -s scripts/tests -p test_project_bootstrap.py -v`:
  **30 passed**. Includes copied guide, engineering version, hashes, discovery,
  portable paths and unchanged retry.
- `python3 -m unittest discover -s scripts/tests -p test_project_templates.py -v`:
  **28 passed**. Includes every application family, guide links/hashes,
  provider inventory/byte parity and existing missing-resource/collision guards.
- `./scripts/check-repository.sh`: local run ended with exit 143 before completion;
  693 completed-suite tests reported no failures. No local full-gate pass is
  claimed. The complete gate passed in source-head GitHub CI, as recorded below.
- `git diff --check` and `git diff --cached --check`: passed in both worktrees.
- Changed Markdown relative-file links, root AGENTS size and `bash -n` over
  executable `sh` examples: passed. Dogstats guide links additionally verified
  through GitHub against the published branch; its guide content matches local.

Terraform tests were not run locally; the source-head CI ran them successfully.
Application builds and live emulator/device checks were not run locally for this
guidance-only extension. Upstream #109/#111/#112 observations are
attributed history, not new runtime evidence. Runner availability, core app flows,
physical GPS/battery/background behavior, retained-data stop/start and observed
shutdown remain their separately recorded acceptance work.

## Hosted CI at implementation revision 4343333

The [Terraform development-host workflow](https://github.com/danielbardsley/gptclaw/actions/runs/41232488766)
**passed**, including the complete repository gate, Terraform format/init/validate
and Terraform tests. Protected remote plan/apply jobs were skipped; no deployment
was performed. The
[federation workflow](https://github.com/danielbardsley/gptclaw/actions/runs/41232488769)
also passed. These results apply to implementation revision `4343333`.

The [quality-template matrix](https://github.com/danielbardsley/gptclaw/actions/runs/41232488778)
failed: metadata and Fastify passed; ten generated-release jobs failed in their
existing dependency-security gates. Inspected job logs show JavaScript audit
findings, mobile unaccepted/expired exceptions, and Python pip_audit findings.
The starter release/dependency bytes are unchanged by this PR; no audit
suppression, exception renewal or dependency change was made. This task did not
rerun a baseline matrix, and does not claim overall CI success.

The [private-application workflow](https://github.com/danielbardsley/gptclaw/actions/runs/41232488786)
also failed. Template and TypeScript API jobs passed. Static-site, multi-service,
mobile/Python integration, development-database and Python API logs show dependency
security checks failing. The mobile-source job reports only a generated-workflow
failure with its internal log path; its precise cause was not exposed in the job
log and is not established here. No broad CI success or baseline reproduction is
claimed. The same dependency-security and opaque mobile-source limitation classes
were previously documented in [SPEC-050 evidence](../050-project-standards-inheritance/acceptance.md).
Final evidence-only commits have their own CI status and require separate review.

## Review and adoption

[GptClaw draft PR #113](https://github.com/danielbardsley/gptclaw/pull/113) and
[Dogstats draft PR #6](https://github.com/danielbardsley/dogstats/pull/6) are open.
Merge, installed-provider rollout and fresh-client instruction discovery remain
pending. New planning bootstrap must select a reviewed revision containing this
bundle; existing projects require explicit adoption. No infrastructure operation,
access grant or SDK/key installation was performed. Rollback is a reviewed
project-owned revert, never an emulator wipe or data reset.
