---
name: gptclaw-project-bootstrap
description: Create a new local planning-ready project from GptClaw with adapted guidance and a copied specification skill. Use for new-project bootstrap, not existing-project adoption, application scaffolding, or ordinary feature work.
---

# Bootstrap a planning project

Use this skill from GptClaw. The output is a local Git repository ready for
planning, not an application, hosted repository, or running service.

Read applicable source and destination guidance and Git status. Obtain name,
purpose, owner, and an explicit destination; infer values already supplied.
Suggest `/srv/forge/projects/<slug>` only when appropriate. The destination's
final component must be a lowercase hyphenated slug; its parent must exist.
Honor the user's existing authorization to create this project. Explain the
concrete path and files before writing; request only missing scope or required
filesystem permission. Never broaden permissions after a denial.

Use the reviewed helper at `scripts/bootstrap-project.py` from GptClaw's root.
Select a locally available, full 40-character commit SHA containing the approved
starter and specification skill. Verify approval/merge evidence; a SHA alone is
not approval. During feature evaluation a clearly identified candidate commit
is allowed in task-owned synthetic fixtures. Do not fetch arbitrary templates.

Run `python3 scripts/bootstrap-project.py --help` to inspect exact arguments.
Invoke it with `--source-revision`, `--destination`, `--name`, `--purpose`, and
`--owner`. Pass values as literal arguments, never executable shell text. A
`--check` invocation previews validation and detects conflicts without writes;
then repeat without `--check` for an already-authorized creation. The helper
prints the canonical destination and source revision before changing files.

The helper reads a fixed allowlist from Git objects, not dirty source files.
It creates README.md, AGENTS.md, .gitignore, documentation index/catalogue,
bootstrap provenance, and the complete `.agents/skills/gptclaw-specification/`
package. It initializes main with no commit or remote and installs no packages.
Normal automatic selection remains enabled; no global settings are changed.

If creation fails, stop and inspect the reported destination and conflict.
Only the helper's temporary staging area is automatically cleaned. An incomplete
project retains `.gptclaw-bootstrap-in-progress` and any already-published files;
never remove an uncertain directory or reset/clean it to retry. A completed,
unchanged output can be checked/retried without writes; modified, incomplete,
occupied, nested-repository, or symlink destinations require separate reviewed
adoption/recovery work. Do not silently overwrite files or switch destinations.

Report actual checks, created paths, source revision, Git state, and limitations.
Ask the user to open the new project in the supported client and verify copied
skill discovery; do not create a user-owned chat without a request. Plan its
first feature only if requested with sufficient scope. A copied file does not
prove client behavior. No original checkout is needed for later specification
writing, and no GptClaw backlog or approval history belongs in the new project.

For future updates, compare source provenance with local adaptations and prepare
a project-owned reviewed diff. There is no synchronization or repair mode.
Reverting this bootstrap implementation does not delete already-created projects.
