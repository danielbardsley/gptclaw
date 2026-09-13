# Adapt repository guidance

The [template](AGENTS.md.template) is an inert, stack-neutral starting point for
a root `AGENTS.md`. Daniel owns the canonical template and GptClaw adoption;
each other repository's owner owns its adaptation. Version 1.0.0 establishes the
six sections below. A source version records ancestry, not identical contents.
The [GptClaw adoption](../../AGENTS.md) and
[synthetic example](../../scripts/tests/fixtures/repository-agents/AGENTS.md.fixture)
show two different projects. Neither example is a default stack to install.

## Inspect before adapting

1. Inspect Git status and preserve unrelated/uncommitted work. Locate the
   repository root and applicable root/area guidance and overrides, including
   untracked files. Do not replace an existing policy or unknown override.
2. Confirm the actual remote launch profile and installed client version. Inspect
   only instruction-related settings: `CODEX_HOME`, `project_doc_max_bytes`,
   `project_doc_fallback_filenames`, and applicable override presence. Do not dump
   environments, complete configuration, authentication, or session logs.
3. Check discovery against the supported client and current
   [official guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
   Checked 2026-09-12: guidance is assembled at run/session start, using global
   guidance followed by project-root-to-working-directory files. Overrides are
   preferred and nearer guidance takes precedence. The documented default
   combined limit is 32 KiB. Inspect effective settings and verify actual loading;
   do not raise limits, change profiles, or remove overrides automatically.
4. Read the existing spec, design, tasks, README, package/version/lock files,
   scripts, and workflow needed to establish project facts. If information is
   missing, name the limitation, owner, and next verification step. Architecture
   defaults are not evidence that a command or tool exists.

Keep the template and adopted policies at most 8 KiB UTF-8 each. Check the
combined instruction budget separately; individually small files can still be
truncated or shadowed. Repository guidance supplies project facts alongside host
agreements and higher-priority session instructions; it cannot grant permissions
or enforce a security boundary. Report unresolved conflicts and continue
unaffected authorized work.

## Adapt in a reviewed branch

Create a feature branch or isolated worktree. Write a candidate beside the
existing policy if one exists and reconcile differences in a reviewable diff;
never blindly copy over it. If no policy exists, adapt the template to a new root
`AGENTS.md`. Rename the metadata field `Template-Version` to
`Source-Template-Version`, retaining the starting version and `Template-Source`.
Do not install this template into the global Codex profile.

Resolve every `{{UPPER_SNAKE_CASE}}` placeholder:

| Placeholder | Required project evidence |
|---|---|
| `PROJECT_NAME` | The actual project name. |
| `PROJECT_PURPOSE_AND_OWNER` | Purpose, intended user/outcome, accountable owner. |
| `STACK_VERSION_SOURCES_AND_LAYOUT` | Actual stack, links to existing version/lock sources, important directories. Avoid duplicate pins. |
| `COMMAND_TABLE` | The operation table described below, including justified not-applicable operations. |
| `PLANNING_AND_REVIEW_REFERENCES` | Where active specs/designs/tasks are found, branch/worktree and PR workflow, acceptance location. |
| `DATA_RULES_AND_PRODUCT_BOUNDARIES` | Allowed data/fixtures, sensitive/generated Git exclusions, runtime-data locations or explicit absence, private access, deployment and destructive-operation boundaries. |
| `GUIDANCE_OWNER_AND_PROCEDURE` | Project policy owner, review/update/rollback procedure or local guide link, fresh-task verification responsibility. |

Keep every required section; explain inapplicability rather than removing it.
Use real repository-relative links for detail and keep essential rules in the
root file. A project outside GptClaw must not depend on a link into GptClaw's local
checkout. `Template-Source` is a provenance identifier, not a required local path.
Version equality never proves that a project adopted later changes.

For each setup, startup, build, format/lint, type-check, test, other quality, and
deployment operation, record directory, exact command or justified
not-applicable entry, prerequisites, side effects, and when to run it. Trace each
command to checked-in sources. Separate local checks from dependency downloads,
service startup, and protected operations. Inspect scripts before classifying
side effects; never run deployment/destructive commands to verify documentation.
Do not add tools or a test coverage target solely to fill a table row.

Select checks based on changed files and behavior. Routine documentation does
not require infrastructure execution. Preserve existing permission and release
gates and prior scope authorization. Copying guidance does not extend any past
temporary exception; exceptions need owner, scope, reason, expiry, and removal.

## Validate and review

For GptClaw, run from its root:

```sh
python3 scripts/tests/test_repository_agents.py
./scripts/check-repository.sh
git diff --check
git diff --cached --check
```

The repository checker includes the focused suite; a separate focused invocation
is useful while editing, not required duplication at handover. It needs Python 3
and Git, uses temporary synthetic fixtures, and performs no network operations.
Its validator only reads the explicit policy and checks local link existence.
Separate tests execute the known synthetic verification script and fixed Git
rollback operations; no command is discovered or executed from policy text.
It does not read linked file contents or credentials.

Validation checks required nonempty sections, byte limit/UTF-8, version/source
metadata, resolved placeholders, and inline Markdown link targets. Supported
links are `[label](relative/path)` with optional fragments or URL-encoded spaces,
fragment-only links, and HTTP(S) links. Local targets must exist within the
explicit repository root, including after symlink resolution. Titles, absolute
paths, reference-style links, queries on local links, and other URL schemes are
unsupported. Anchors and external URLs are not validated or fetched. Fenced
examples are excluded from section/link checks; this is a narrow authoring
convention, not a general Markdown parser or security audit.

For another project, apply this same checklist manually or adapt the focused
checks in its reviewed workflow; this feature adds no universal validator CLI.
Human review must verify meaning, command correctness, complete applicability,
data constraints, conflicts, and preservation of existing guidance. Passing
static checks cannot establish permission safety or actual instruction loading.

## Fresh-task acceptance

After review of the adopted revision, start a new task through the supported
remote project connection at each project root. Existing conversations, a local
CLI run, and manually pasted policy text do not satisfy this gate. Use an
explanation-only prompt with tools disabled or the supported read-only mode:

> Without executing commands or changing files, identify this project's purpose,
> owner, loaded instruction sources, checks for a documentation-only change and
> a behavior change, allowed data, and deployment boundaries. Explain how project
> guidance relates to host guidance and previously authorized work. State any
> missing or conflicting instructions.

Evaluate against each adopted file without giving the task the expected answers.
Record the reviewed commit, project root, client/version and relevant profile
metadata, date, scenario outcomes, and limitations. Retain sanitized summaries,
not complete configuration or raw session logs. Resolve missing/shadowed guidance
through review, preserve unknown files, and repeat affected checks in new tasks.

To prepare the second project, run the following in GptClaw's root. This creates
only a uniquely named scratch directory and local Git repository; no remote,
credentials, dependencies, or service are involved:

```sh
agt002_fixture_dir=$(mktemp -d /tmp/gptclaw-agt002-remote.XXXXXX)
cp scripts/tests/fixtures/repository-agents/README.md "$agt002_fixture_dir/README.md"
cp scripts/tests/fixtures/repository-agents/verify.py "$agt002_fixture_dir/verify.py"
cp scripts/tests/fixtures/repository-agents/AGENTS.md.fixture "$agt002_fixture_dir/AGENTS.md"
git -C "$agt002_fixture_dir" init --quiet
python3 "$agt002_fixture_dir/verify.py"
```

Record that task-owned path and select it through the same supported connection.
The expected project is Pebble Counter, not GptClaw. If the connection cannot open
the scratch root, record AC-005 as pending and arrange a supported project path;
do not claim CLI verification is equivalent or change host security controls.
Keep the fixture until evidence is recorded, then remove only that confirmed
scratch directory. Never clean another project's working tree.

## Update and rollback

Compare the adopted source version with the new canonical template in Git.
Review each difference, preserve project-specific facts and later user edits,
incorporate relevant changes, and update `Source-Template-Version` deliberately.
Template edits do not synchronize other repositories or the installed host
policy. Bump the canonical semantic version when changing the contract: major
for incompatible authoring requirements, minor for compatible additions, patch
for corrections. Recheck affected adoptions and document intentional divergence.

Before rollback, inspect status and the exact adoption/update commit. Prepare a
reviewed targeted `git revert` of that commit on a feature branch. If it conflicts
with later policy edits, reconcile those edits explicitly; never reset, clean,
or overwrite the entire file with an old copy. For a first adoption, the revert
removes only the introduced policy; for an update, it restores prior instructions.
Preserve unrelated committed and uncommitted work. Run checks applicable to the
result and verify in a fresh task after the reviewed change. A first-adoption
removal intentionally ends repository-template validation for that project and
requires a matching reviewed adjustment to any check that requires the file.

The focused suite rehearses update and first-adoption reverts in isolated Git,
proving that unrelated later documentation and an uncommitted note survive.
The operator still owns live rollback and fresh-task evidence. See
[SPEC-004 acceptance](../../docs/004-repository-agents-template/acceptance.md)
for current status; AGT-001's separate acceptance is not completed by this work.

## Focused area guidance

Use the [nested guidance pattern](nested/README.md) when an existing subtree has
durable local conventions. It supplies an independent 4 KiB area contract and
explicit discovery for root-started work; the root contract stays within 8 KiB.
