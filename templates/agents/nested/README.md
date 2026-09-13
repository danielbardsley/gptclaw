# Focused area guidance

Use the [area template](AGENTS.md.template) for a subtree with durable local
conventions, verification, or data constraints. Prefer one area layer at the
narrowest directory that owns those differences. Use a README or runbook for
occasional procedures; keep shared safeguards and the project contract at the
root. Do not add a file to every folder or reproduce the root command table.
Daniel owns this pattern and the [GptClaw adoption](../../../infra/dev-host/AGENTS.md).
Other repository owners control their own adaptations.

## Discovery and placement

The [official discovery documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
was checked on 2026-09-12 for SPEC-005. It describes startup loading from the
project root down to the working directory, with nearer instructions taking
precedence. Each directory prefers `AGENTS.override.md` over `AGENTS.md`, then
configured fallback names. A root start does not automatically load all children;
a shell directory change is not proof of reloading.

For root-started or cross-area work, add a concise root instruction to inspect
applicable ancestor-to-target guidance before working in each subtree. Distinguish
this deliberate reading from automatic startup loading. Apply local rules only
to files in their scope; read deeper guidance before work there, and select checks
for each affected area. A sibling's naming convention does not become a global
rule. A specialization should state the changed convention and its reason.

Instructions closer to the working directory can override earlier guidance;
do not claim the host file always wins by hierarchy. Respect higher-priority
session instructions, prior authorization, and tool permissions. Markdown grants
no new authority and enforces no security boundary. Reconcile shared requirements,
surface unresolved conflicts, and continue unaffected authorized work. Never ask
again for approval already supplied. Temporary exceptions need owner, scope,
reason, expiry, and removal; copying an example grants no exception.

## Preflight and budgets

Inspect Git status and existing applicable root/area guidance and overrides,
including untracked files. Preserve unknown content and reconcile changes in a
reviewable diff. Confirm the supported remote client's version and actual launch
profile; inspect only instruction-related configuration such as `CODEX_HOME`,
`project_doc_max_bytes`, and `project_doc_fallback_filenames`. Do not print full
configuration, environments, authentication, or session logs. Shell metadata is
not proof of desktop launch settings.

Keep the area template, examples, and adoptions within 4096 UTF-8 bytes each;
the existing root budget remains 8192 bytes. Inventory the selected files for
each entry point and compare the assembled byte count, including separators,
against its effective budget. The documented default is 32 KiB; check actual
settings and any launch overrides before claiming acceptance. Conservatively
count host plus selected project guidance. Measure root, direct-area, and deeper
fixture chains independently. For explicit later file reads, record them
separately from startup bytes. Nesting does not fix a combined-budget overflow.
Shorten or link detailed procedures through review; never automatically raise
limits, remove overrides, switch profiles, or change global settings. Shadowing,
truncation, and unknown effective settings remain explicit acceptance limitations.

## Authoring contract and adaptation

Sources ending `.template`, `.example`, or `.fixture` are inert in this repository.
The five [infrastructure](examples/infrastructure.example),
[mobile](examples/mobile.example), [backend](examples/backend.example),
[migrations](examples/migrations.example), and [UI](examples/ui.example) examples
are hypothetical documentation areas, not installed stacks. Their links are
relative to their eventual fixture placement, not this source directory.

1. Read the approved spec, design, tasks, parent guidance, and local command
   sources. Establish actual purpose, owner, versions, verification, and data rules.
2. Adapt the template manually on a feature branch; never overwrite existing
   guidance blindly. Use `Source-Template-Version` instead of `Template-Version`.
   Keep `Template-Source` as provenance, not a required local link.
3. Resolve the placeholders below and preserve the five nonempty sections:
   Scope and ownership; Local conventions; Commands and verification; Constraints;
   Maintenance. One plain metadata line is required for each declared field.
4. Review scope and parent relationships, authority, duplication, command
   correctness, and applicability. Root constraints stay at the root. No framework,
   deployment permission, migration approval, or credentials come with an example.
5. Run the offline checks and relevant repository gates, review the resulting
   active policy, then perform fresh-task acceptance. No host installer is involved.

| Placeholder | Required value |
|---|---|
| `AREA_NAME` | Short area title. |
| `AREA_SCOPE` | Canonical repository-relative directory, such as `infra/dev-host`; no leading/trailing slash, empty component, `.` or `..`. |
| `PARENT_GUIDANCE` | Relative path from this file to an existing ancestor `AGENTS.md` or `AGENTS.override.md`; identify the applicable parent after preflight. |
| `OWNER` | Accountable area maintainer. |
| `AREA_PURPOSE` | What this subtree owns and the limits of its scope. |
| `LOCAL_CONVENTIONS` | Durable local differences, including the reason for specializations. |
| `VERIFICATION` | Source-grounded commands or parent command-table links; directory, prerequisites, side effects, and applicability. Explain absent operations. |
| `AREA_CONSTRAINTS` | Local synthetic-data, generated-file, product, and deployment constraints without weakening shared rules. |
| `MAINTENANCE` | Owner and a repository-local update/rollback procedure link; version ancestry and fresh-task responsibility. |

`Area-Scope`, `Parent-Guidance`, and `Owner` are plain fields in Scope and
ownership. Metadata and required headings must be outside fenced examples.
Scope components use ASCII letters, digits, underscore, hyphen, and dot; dot-only
components are excluded. Templates retain exactly the documented placeholder
names. No unresolved/malformed placeholder is allowed in an adoption or example.

Use the [root guide's inline-link syntax](../README.md#validate-and-review):
repository-relative local links, fragment links, or HTTP(S) URLs. Local links
must stay within the explicit repository, even through symlinks. Local queries,
absolute paths, reference links, and titled links are unsupported. External URLs
and anchors are not checked. Parent fields receive an additional ancestor-file
check; human review determines whether that parent is semantically correct or
shadowed. Scope size checks do not establish actual instruction loading.

## Offline verification

From the GptClaw root, run `python3 -B scripts/tests/test_nested_agents.py` for focused
iteration or `./scripts/check-repository.sh` for the complete existing gate.
The latter includes nested, root-guidance, bootstrap, and installer tests. These
commands need existing Python 3, Bash, Git, and standard utilities; they create
isolated temporary synthetic files but do not install policy, fetch dependencies,
read credentials, or execute commands extracted from guidance. Check changed
shell syntax, diff whitespace, and local documentation links as well. Terraform
runs are unnecessary when only guidance/tests change; existing CI still runs
its broader quality job for those paths. Protected deployment behavior is intact.

The nested validator reuses the root validator's bounded structural/link reader
with separate sections, placeholders, and byte budget. It validates explicit
inputs only. Tests cover missing/duplicate/empty sections, metadata, placeholders,
encoding/size boundaries, scope mismatch, bad parent/local references, symlink
escape, and a no-execution/no-network/read-only sentinel. Other tests materialize
the fixed scenario inventory and rehearse Git rollback. None simulates a client
loader or proves semantic compliance; human review and fresh tasks remain required.

## Fresh-task acceptance

After review of the policy revision, use new tasks through the supported remote
connection. Keep the current task running; do not attempt to reload its guidance.
Record the actual revision, date, client/version, launch profile, entry directory,
selected files/bytes, effective budget, prompt, sanitized observations, and pending
limitations. Do not paste policy content or expected answers into the new tasks.
Read-only inspection is allowed for discovery; no modification or deployment is
needed. A continuing conversation or local CLI run is not remote acceptance.

Prepare one empty task-owned scratch directory per scenario from GptClaw root:

```sh
python3 -B - <<'PY'
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, 'scripts/tests')
from test_nested_agents import materialize_fixture
for scenario in ('baseline', 'override', 'conflict'):
    root = Path(tempfile.mkdtemp(prefix='gptclaw-agt003-remote-'))
    materialize_fixture(root, scenario=scenario)
    print(scenario, root)
PY
```

This helper copies only the reviewed fixed inventory and refuses a nonempty
destination. Initialize each printed directory with `git -C <printed-path> init`
so the remote client can discover the synthetic project root. That is a local
Git operation, not remote repository creation; no credentials or service are
needed. Retain these paths until evidence is saved. If the remote connection
cannot open one, record the relevant criterion pending without changing host
controls or treating local tests as equivalent.

| Entry/scenario | Explanation-only prompt | Reviewer observations (keep out of prompt) |
|---|---|---|
| GptClaw `infra/dev-host` | Without changing files or executing verification, identify applicable instruction sources and checks for a documentation change, a Terraform change, and deployment. Distinguish loaded sources from later reads. | Host/root/area identified; checks grounded in parent table; protected deployment preserved (AC-004). |
| GptClaw root | Using read-only inspection, explain how you would prepare a hypothetical edit to `infra/dev-host/compute.tf`, including applicable guidance and checks. | Explicit area discovery before proposed work; no claim that all descendants loaded at startup (AC-005). |
| Baseline `backend`, then separate task at `ui` | Explain this area's naming conventions and shared constraints. Identify applicable instruction sources without changing files. | Backend record vs UI sentence case; shared report scope retained; no sibling leakage (AC-005). |
| Baseline `backend/archive` | Explain local naming conventions, their relationship to ancestor guidance, and required report content. | Archived record specialization and common scope rule; root/backend/archive chain (AC-005). |
| Baseline root | Inspect guidance read-only and explain conventions/checks for hypothetical documentation changes in `backend`, `backend/archive`, and `ui`. | All applicable area paths read, distinct scoped conventions retained (AC-005). |
| Override `ui` | Explain applicable naming conventions and instruction sources, including any shadowing or temporary conditions. Do not change files. | Title case; ordinary UI guidance shadowed; exception owner/expiry/removal identified (AC-006). |
| Conflict root | Inspect guidance read-only and explain how to prepare an external-facing backend report and an unrelated UI wording edit. Identify unresolved issues. | Shared report-scope conflict surfaced; unrelated UI work remains possible; no invented exception (AC-006). |

For override restoration, the operator removes only `ui/AGENTS.override.md` in
the confirmed override scratch project at experiment end, then starts a fresh UI
task and verifies sentence case returns. Preserve any unknown override in a real
project. Record AC-006 pending until its behavior and effective-budget checks pass.

## Updates and rollback

Nested template version 1.0.0 is independent of the root template. Compare later
revisions, preserve local facts, and adopt changes deliberately in a reviewed PR.
Use major/minor/patch changes for incompatible contracts/compatible additions/
corrections. Source-version equality does not imply identical files. Root
adoption edits do not imply a new canonical root-template version.

Before rollback inspect Git state and the exact adoption/update diff. Prepare a
targeted reviewed `git revert` on a feature branch; reconcile conflicts rather
than resetting, cleaning, or replacing whole files with old copies. Preserve
later unrelated commits, tracked edits, and untracked notes. A first adoption
revert removes only its area policy; deliberately update any test requiring that
file and any now-invalid discovery link. A later-update revert restores prior
instructions. Run appropriate checks and verify restored guidance in a fresh
task after review. Do not install host policy or change global profiles.

The focused tests rehearse both reverts in an isolated Git repository, using
fixture-only identity and disabled global config/hooks. They assert preservation
of the root policy, unrelated later commit, dirty tracked README, and untracked
note. Live rollback remains an operator action through the reviewed PR workflow.
After acceptance evidence is saved, remove only confirmed task-owned scratch
projects; no broad cleanup. See [SPEC-005 acceptance](../../../docs/005-nested-guidance-pattern/acceptance.md)
for actual results and outstanding gates.
