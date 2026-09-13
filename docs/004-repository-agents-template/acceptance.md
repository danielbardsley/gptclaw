# ACCEPTANCE-004: Repository AGENTS.md Template

- **Status:** Implementation reviewed and merged; CI and remote acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-004](./spec.md)
- **Technical design:** [TDD-004](./technical-design.md)
- **Tasks:** [TASKS-004](./tasks.md)
- **Review:** [PR #9](https://github.com/danielbardsley/gptclaw/pull/9)
- **Last updated:** 2026-09-12

## Authorization and baseline

Daniel approved the specification and requested implementation on 2026-09-12.
He subsequently reviewed the resulting PR and explicitly authorized its merge.
[PR #9](https://github.com/danielbardsley/gptclaw/pull/9) merged as
`05cfbb7c7590fc4b908dd62519b62d3696498620`, with approved head
`af015bb6bfb414ca60effd8368fcebca5c824985`. Fresh-task acceptance remains separate.

The working tree was clean at implementation start. No GptClaw root policy or
root override existed. The existing `config/codex/AGENTS.md` host source was
preserved. No host policy installation, global settings change, credentials,
infrastructure mutation, or service operation was performed.

Preflight found `codex-cli 0.153.4` and shell `CODEX_HOME=/home/forge/.codex`.
Global policy existed; global/root overrides and ancestor policies under
`/srv`, `/srv/forge`, and `/srv/forge/projects` were absent. No explicit
`project_doc_max_bytes` or `project_doc_fallback_filenames` setting was found in
the profile config. Only matching non-secret settings and file-presence metadata
were inspected; authentication and full configuration were not printed.

[Official instruction discovery guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
was checked on 2026-09-12. The profile observations and size checks do not prove
the actual remote instruction chain; AC-005 remains pending. AGT-001's separate
acceptance record remains unchanged.

## Acceptance mapping

| Criterion | Evidence and remaining work |
|---|---|
| AC-001 | Template and guide cover six required sections; GptClaw and Pebble Counter include source version 1.0.0. Static checks pass. Template is 3,082 bytes; GptClaw policy 7,640 bytes; fixture policy 3,466 bytes. Daniel reviewed the resulting policy and authorized merge. |
| AC-002 | Command map reviewed against README, scripts, version/lock files, and existing workflow. Python/Bash/Git offline commands are available. No Terraform executable is on this shell's PATH; Terraform was not installed or run locally. CI results are recorded below. |
| AC-003 | Ten focused tests pass: shipped contracts, full template adaptation, missing/duplicate/empty sections, placeholders/metadata, byte limits/encoding, invalid links, symlink escape, no command/network execution by validation, synthetic verification, and targeted Git rollback. |
| AC-004 | Diff adds root guidance, inert template/fixture, tests, guide, documentation, and two workflow path entries per event. Existing guidance and deployment gates are unchanged. Daniel reviewed and authorized the resulting PR merge. |
| AC-005 | Pending fresh tasks through the supported remote connection at GptClaw and the synthetic project root. This continuing task and CLI metadata are not qualifying evidence. |
| AC-006 | Automated isolated Git rehearsal reverts an update, restores prior policy bytes, then reverts first adoption; unrelated later README changes and an uncommitted user note survive. Manual version comparison, review, rollback, and fresh-task procedure are in the guide. Owner review is complete. |
| AC-007 | This record captures local evidence. Implementation is reviewed and merged at the revision above. CI, remote results, and final acceptance remain pending; catalogue stays Planned with merged status explained. |

## Command review

- Terraform version and provider pins link directly to the existing declarations.
  Initialization follows the CI flags, including `-lockfile=readonly`; it is
  identified as network-dependent setup. No local apply command is offered.
- `scripts/check-repository.sh` runs host-policy, bootstrap, and now repository
  guidance checks. The guide distinguishes validation from the explicit tests
  of known synthetic code and fixed Git rollback operations.
- Development startup/build and separate type/lint tools are explicitly
  inapplicable to this infrastructure repository. No future runtime is assumed.
- Documentation-only checks remain proportionate. The workflow's existing
  broader quality job is retained; only path filters change. No protected
  workflow dispatch was triggered by this implementation.

## Local verification

- `python3 scripts/tests/test_repository_agents.py`: 10 tests passed.
- `./scripts/check-repository.sh`: passed all repository invariants and 32 tests
  (17 host-policy, 5 bootstrap, 10 repository-guidance).
- `bash -n scripts/check-repository.sh` and `git diff --check`: passed.
- Relative-link review: all 57 local links across nine changed documentation
  files resolve; the documented example link syntax is excluded.
- Installed host plus root policy size: 12,727 bytes by file metadata, below
  the documented default combined budget; actual loading remains unverified.
- Terraform format/init/validate/test: not run locally; no Terraform executable
  on PATH and no infrastructure source changed. CI retains the full quality job.
- Initial focused run caught the not-yet-created guide link; after the guide was
  written all focused tests passed.
- Git rollback fixtures are created and cleaned by `TemporaryDirectory`; no
  unrelated project is scanned or modified.

## CI and remote verification

Implementation revision: `770c06f0debb3991250b82ee8115bc2234dd193c`
([commit](https://github.com/danielbardsley/gptclaw/commit/770c06f0debb3991250b82ee8115bc2234dd193c)).
Local results above were run against those implementation bytes.

[CI run #53](https://github.com/danielbardsley/gptclaw/actions/runs/34725555902)
for that revision is pending with no jobs started at handover. This is not a CI
pass. No queued run was cancelled and no deployment workflow was dispatched.
This subsequent evidence-only commit changes no implementation or test bytes.

No new-task creation tool is available in this session. Fresh remote tasks were
not simulated with a CLI run or by reusing this conversation. After resulting
policy review, follow the [guide](../../templates/agents/README.md) to prepare
the disposable project and open both roots through the supported connection.
The guide includes an explanation-only prompt without expected answers and
the evidence fields to record. No live scratch project is left behind yet.

The final PR head
[CI run #54](https://github.com/danielbardsley/gptclaw/actions/runs/34725653236)
was also pending when merge was requested. GitHub accepted a normal merge with
the expected head SHA; no required-check override or admin bypass was used.

Daniel owns the remaining remote acceptance. Record CI results and sanitized
fresh-task outcomes before marking AC-005/007 passed or AGT-002 Delivered.
