# SPEC-005: Nested Guidance Pattern

- **Status:** Draft; not approved for implementation
- **Owner:** Daniel
- **Feature catalogue:** AGT-003
- **Technical design:** [TDD-005](./technical-design.md)
- **Implementation tasks:** [TASKS-005](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), section 9
- **Last updated:** 2026-09-12

## 1. Summary and desired outcome

Provide a reusable pattern for focused area `AGENTS.md` files. An agent working
in infrastructure, mobile, backend, migrations, or UI should find the relevant
local commands and constraints while retaining repository-wide guidance. Area
rules should stay scoped to their subtree and avoid enlarging the root policy
with details that only apply to one part of a project.

The first proposed adoption is `infra/dev-host/AGENTS.md` in GptClaw. Other
areas are demonstrated with inert examples and synthetic fixtures, not new
application stacks. This draft defines future implementation; creating or
merging these planning documents does not approve policy adoption.

## 2. Scope and dependencies

### Included

- A stack-neutral area template, placement and adaptation guide, and concise
  inert examples for infrastructure, mobile, backend, migrations, and UI.
- One GptClaw infrastructure adoption and a small root-guidance discovery pointer.
- Narrow offline authoring checks, synthetic hierarchy fixtures, and fresh-task
  acceptance scenarios for automatic loading and explicit area discovery.
- Version provenance, ownership, review, update, and rollback procedures.

### Excluded

- Host-policy installation, bootstrap changes, global client settings, new
  permanent overrides, or migration of existing policies in other projects.
- Application scaffolding, stack installation, skills (AGT-004 onward), a general
  context validator (AGT-010), automatic synchronization, or a policy engine.
- Changes to Terraform behavior, deployment gates, credentials, infrastructure,
  runtime services, production dependencies, public access, or real datasets.
- Completion claims for AGT-001 or AGT-002's outstanding acceptance work.

[SPEC-003](../003-reviewed-host-agents/spec.md) provides the host-policy baseline;
[SPEC-004](../004-repository-agents-template/spec.md) provides the merged root
contract, inert-template convention, and existing offline checks. Their
acceptance remains independently tracked. Drafting and isolated tests can
proceed; final AGT-003 acceptance must demonstrate host, root, and area guidance
together through the supported remote connection. No future platform tool is
a prerequisite.

## 3. Proposed defaults

| Item | Default for review |
|---|---|
| Reusable sources | `templates/agents/nested/`, using `.template` or `.example` filenames that do not activate instructions |
| Active first adoption | `infra/dev-host/AGENTS.md`; no additional active area policies |
| Placement | At the narrowest existing directory that owns a distinct, durable set of rules; no mandatory file per folder |
| Content budget | At most 4 KiB UTF-8 per area template, example, and adoption; preserve the existing 8 KiB root budget |
| Hierarchy | Prefer one area layer; demonstrate a deeper specialization in a synthetic fixture only |
| Distribution | Manual adaptation and reviewed PR; project owners control later updates |
| Review owner | Daniel for the pattern and GptClaw adoption |

## 4. Requirements

### NAG-001: Focused area contract

Each area template/adoption must identify its directory scope, purpose, owner,
parent guidance, source version, local rules, applicable verification, and
maintenance references. Include only facts that differ from or specialize the
parent contract. Preserve essential repository-wide instructions at the root;
do not move safeguards into a file that root-started tasks might never load.
Use relative links for detail and resolve authoring placeholders before adoption.

The guide must explain when a nested file is useful and when an existing README,
runbook, or root entry is sufficient. Examples must cover all five catalogue
areas without assuming a framework, toolchain, database, or service is installed.

### NAG-002: Discovery and scope across task entry points

Document automatic startup loading separately from deliberate reading of area
files while working. The current official documentation describes a startup
chain from the project root to the working directory, with nearer instructions
taking precedence; a root start does not automatically include every descendant.
At each directory, override files take priority over ordinary guidance. These
are documented expectations to verify against the supported client, not proof
of this host's behavior. [Official discovery reference](https://learn.chatgpt.com/docs/agent-configuration/agents-md), checked 2026-09-12.

Provide a short root instruction to inspect applicable ancestor-to-target area
guidance before work in a subtree, including when a task crosses into another
area. Apply each area's rules to its own files; do not carry a sibling's local
commands into unrelated work. Do not assume a shell directory change reloads
instructions. Tasks spanning areas must reconcile shared requirements, select
checks for each affected area, and surface unresolved conflicts while continuing
unaffected authorized work.

Preflight must inspect existing applicable guidance, override presence, client
version, and only necessary instruction-loading settings. Preserve unknown
files and settings; do not remove overrides or increase limits automatically.

### NAG-003: Clear authority and safe specialization

Allow local conventions and verification commands to specialize root defaults
where appropriate, with the difference and its reason explicit. Do not claim
that host text always wins by hierarchy, or that Markdown enforces permissions.
Respect higher-priority instructions, session authorization, and actual tool
permissions. Area guidance grants no infrastructure, secret, production, or
public-exposure authority and must not silently weaken project constraints.

Distinguish routine local specialization from unresolved policy conflicts.
Existing authorization remains valid; the pattern must not introduce repeated
approval questions for already-authorized work. Temporary exceptions need an
owner, scope, reason, expiry, and removal step; examples grant no exceptions.

### NAG-004: Grounded adoption and compact instruction chains

Derive the infrastructure adoption from existing Terraform version/lock files,
README, scripts, tests, and workflow. Declare working directory, prerequisites,
side effects, and applicability for any local command added; link to shared
commands instead of maintaining a second full root command table. Preserve
committed code -> GitHub Actions -> HCP Terraform -> AWS and the distinction
between documentation checks, offline checks, provider setup, and deployment.

Measure individual file sizes and assess the effective combined loading budget
for each accepted entry point. More nesting must not be presented as a remedy
for exceeding that combined budget. Resolve oversize content by editing and
linking detail through review. Record shadowing or truncation as acceptance
failures or pending limitations rather than treating file presence as loading.

### NAG-005: Reviewable maintenance

Keep reusable sources inert and record template/source versions in deliberate
adoptions. Version equality records ancestry, not identical contents. Root
changes must retain compatibility with SPEC-004's contract and existing tests.
Inspect the working tree and reconcile existing content before adoption; do not
install or update the global host policy. Canonical updates do not synchronize
adopted files automatically.

Document and rehearse targeted Git reverts for first adoption and later updates
in isolated fixtures, preserving unrelated subsequent and uncommitted work.
Verify changed or restored guidance in fresh tasks; do not reload ongoing tasks.

### NAG-006: Verification and honest evidence

Extend existing standard-library checks only as needed for explicit shipped
files and synthetic fixtures. Check nonempty required sections, scope and parent
references, provenance, placeholder resolution, UTF-8 byte limits, and local
link existence. Negative cases must catch malformed or missing contract content,
broken references, and oversize files. Validation must not execute policy command
text, read credentials, fetch dependencies, or scan unrelated projects.

Use human review for semantic scope, command correctness, duplication, and
conflicts. Use fresh-task behavior for actual discovery and instruction use;
static tests are not a replacement. Record sanitized revision, client/profile,
entry directory, scenario, result, and limitations in acceptance evidence.

## 5. Acceptance criteria

| ID | Required evidence |
|---|---|
| AC-001 | Reviewed inert template, guide, and five area examples satisfy NAG-001–005; adopted placeholders are resolved and file budgets pass. |
| AC-002 | GptClaw infrastructure adoption and root discovery pointer are reviewed against checked-in commands and constraints; existing root contract remains valid and no host/runtime/infrastructure changes occur. |
| AC-003 | Offline positive and negative fixtures pass, including a command sentinel proving policy text is not executed; checks remain scoped to explicit test inputs. |
| AC-004 | Fresh task started directly in `infra/dev-host` through the supported connection identifies host, root, and area sources and correctly distinguishes documentation, Terraform verification, and protected deployment. No policy text is pasted into its prompt. |
| AC-005 | Fresh root-started task discovers infrastructure guidance before a hypothetical area change. Synthetic fresh tasks demonstrate two siblings, a deeper specialization, and a cross-area change, applying rules only to their intended files and retaining shared constraints. |
| AC-006 | Synthetic override-shadowing and conflicting-guidance scenarios are correctly identified; preflight records effective budget and relevant configuration. Unknown files/settings remain intact. Missing loading or truncation cannot pass as success. |
| AC-007 | Isolated first-adoption and update rollback rehearsals preserve unrelated work; ownership, provenance updates, and fresh-task re-verification are documented. |
| AC-008 | Sanitized acceptance evidence maps every criterion to actual local/review/remote results and merged implementation PR; catalogue reports the true state. |

Fresh-task scenarios use synthetic or explanation-only changes, with read-only
inspection where explicit discovery is being tested. They must not execute
deployments, migrations, destructive operations, or deliberately unsafe commands.
A local CLI check does not by itself establish supported remote-client acceptance.
If an entry point cannot be exercised, record the criterion as pending.

## 6. Deliverables and approval

Implementation would deliver the reusable pattern and examples, one active area
policy, the root pointer, focused checks/fixtures, and `acceptance.md` beside these
planning documents. The design and tasks describe that proposed work in order.
Daniel reviews scope, budgets, first adoption, and acceptance expectations before
implementation begins. No implementation approval is recorded by this draft.

Mark AGT-003 Delivered only after the implementation PR is merged and all eight
acceptance criteria pass. This proves one real adoption and reusable examples;
it does not establish adoption in other repositories or completion of earlier
initiatives' acceptance gates.
