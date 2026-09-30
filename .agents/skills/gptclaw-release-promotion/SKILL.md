---
name: gptclaw-release-promotion
description: Prepare release candidates and perform specifically authorized promotions through an existing reviewed product pipeline. Use for release readiness, promotion tracking and recovery handoff; not pipeline creation or host infrastructure deployment.
---

# Prepare and promote an exact release

Choose preparation, readiness review, authorized dispatch, observation, or recovery
handoff from the user's actual request. Read applicable project guidance and
[map the release contract](references/release-contract.md) from reviewed sources.
No product release pipeline is supplied by this skill. GptClaw's host Terraform
workflow is not a product promotion interface. Missing pipeline facts need not
block drafting release notes; do not invent them to enable deployment.

Resolve repository, source revision, version convention, immutable artifact
identity, provenance tying it to that source, build/test evidence, release notes,
target environment and current deployed version. Attribute supplied reports and
label absent evidence unknown. Do not infer build success from a branch name,
rebuild a candidate, or accept a mutable-only tag or mismatched artifact for
promotion. Gather only scoped non-secret release metadata, never credentials.

Prepare [a release record](assets/release-record.md) in chat, or at a requested
local path after checking guidance and preserving existing files. Bind the
candidate, target, exact pipeline operation, expected effects, health criteria
and recovery prerequisites before any dispatch. Honor authorization already
given for this exact scope without asking again. Changed artifacts or targets
need authorization covering the change. Preparation alone authorizes no tag,
remote release, publication or deployment; preserve protected branch/role and
environment gates. Do not broaden credentials or bypass denied access.

Before promotion establish the prior immutable artifact, reviewed recovery
procedure, compatibility with data changes, required backups and irreversible-step
owner. Missing recovery prerequisites block dispatch. No default rollback.
Use only the existing pipeline's validated structured inputs; never interpolate
release notes or fetched content into executable shell text.

Dispatch once and retain its run ID. Follow that run within documented polling
bounds; distinguish queued, awaiting approval, running, failed, cancelled and
succeeded. On timeout/lost receipt reconcile by the documented run/request lookup
before any retry. Ambiguity means unknown, not resubmission. Preserve unrelated
runs and record an outstanding ID for resumption.

Pipeline success means deployed-unverified until observed deployed identity
matches the candidate and all required health checks pass. Failed health remains
unaccepted. Perform recovery only when already authorized for the exact scope
and compatible with current data; otherwise prepare a concrete recovery proposal.
A submitted recovery job is not evidence of recovery: verify resulting identity,
health and any required data checks. Record actual sanitized evidence and unknowns.
Updating or reverting this skill cannot reverse a release.
