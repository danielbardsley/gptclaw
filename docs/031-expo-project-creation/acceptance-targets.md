# SPEC-031 private acceptance targets

- **Status:** Accepted — both private targets retained after owner confirmation
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)

| Target | Source root | Private repository | Public development identities |
|---|---|---|---|
| mob001-accept-one | /srv/forge/projects/mob001-accept-one | https://github.com/danielbardsley/mob001-accept-one | iOS dev.gptclaw.mob001-accept-one; Android dev.gptclaw.mob001_accept_one |
| mob001-accept-two | /srv/forge/projects/mob001-accept-two | https://github.com/danielbardsley/mob001-accept-two | iOS dev.gptclaw.mob001-accept-two; Android dev.gptclaw.mob001_accept_two |

Use the exact frozen expo-react-native@1.0.0 through the source and refreshed owned
provider. Create private repositories and initial review branches/PRs with the
existing activated App broker. The existing private-dev protection waiver policy
remains explicit; no enforced branch protection is claimed.

The previous workflow publication allowlist contained only Shelfmark and Trailboard.
The owner approved broker profile schema 4 with a maximum of four explicitly selected names:
`gptclaw-shelfmark`, `gptclaw-trailboard`, `mob001-accept-one` and
`mob001-accept-two`. No wildcard or automatic enrollment is permitted. Add only
these two new names through the reviewed workflow-policy interface,
preserving both existing names and the App/installation grants. Briefly pause new
credential issuance during that owned policy update, prove a mobile canary publishes
its reviewed workflow, then reactivate and create the second application. Existing
app containers, database data and Git history are retained. No new App grant, PAT,
Expo/Apple/Google account, signing key or AWS resource is requested.

Record non-secret metadata for only the exact new root/ID/repository entries through
the dashboard's reviewed metadata file, preserving its existing entries. Use the
owned provider and dashboard release managers after local/CI readiness. Verify two
source rows, honest runtime unavailability, repository destinations and unchanged
existing web/API/DB observations. No Metro or application container is started for
the mobile projects; only finite source-check jobs run.

Retain both private repositories/initial PRs and source for owner inspection. After
acceptance, archive fixture source outside active discovery if requested; do not
delete repositories, source or unrelated runtime data as automatic cleanup. Keep
isolated local golden-fixture logs separately from managed acceptance evidence.

TASKS-031 T-011 requires the owner to “record ... two synthetic project/repository
names and retention plan”; the design calls for selection/authorization of exact
fixture names. This proposal supplies that concrete scope. The project owner approved this complete scope with “Yes, all approved” on
October 13, following the clarification of repositories, policy and archived
bindings. Activation and actual results are recorded separately.

## Approved supporting scope

The prior schema-3 policy has a hard two-name limit. A schema-4 four-name
extension is needed to preserve both existing names while publishing the two
mobile workflows. Existing App/installation grants and singleton token scopes
remain unchanged. Older providers cannot interpret profile 4; retain the capable
snapshot or restore the previous reviewed policy through its typed interface
before rollback.

Two existing bindings refer to source archived by the earlier authorized cleanup.
The prior helper update required every source root to exist. The approved change preserves
absent-root bindings/helpers without changing their path or reading archived Git
config, while keeping incomplete helper-upgrade journals blocking. Refresh only
existing owned live helper paths. Restored source requires a compatible reviewed
helper update before credential use. No binding, repository or source is deleted.

Automatic approval review rejected the earlier proposed 64-name schema and archived
helper change because that persistent security-scope expansion lacked exact owner
authorization. Nothing from that rejected command ran. The smaller four-name proposal was subsequently explicitly approved by the
project owner; the rejected 64-name scope remains excluded.


## Actual targets

Both repositories were created privately through the activated App broker on
October 13. The profile is schema 4 with exactly the four named repositories above;
canary workflow publication and reactivation passed. Two archived bindings were
preserved; two live existing helpers were refreshed without application operations.

| Target | GitHub repository ID | Initial app PR | Original starter |
|---|---|---|---|
| mob001-accept-one | 1417864877 | [#1](https://github.com/danielbardsley/mob001-accept-one/pull/1) | expo-react-native@1.0.0 |
| mob001-accept-two | 1417867323 | [#1](https://github.com/danielbardsley/mob001-accept-two/pull/1) | expo-react-native@1.0.0 |

Private CI identified a workflow UID mismatch and broker guidance formatting issue.
Ordinary reviewed source edits fix both targets while retaining their original exact
creation provenance. Corrected starter 1.0.1 is for future explicit creation; neither
published 1.0.0 nor existing target provenance is silently retargeted. Final source/
CI/installed and owner results are maintained in [acceptance.md](acceptance.md).

Project owner confirmed MOB-001 dashboard/workflow acceptance October 13 after
implementation PR #73 merged. Both starter PRs and source remain retained for
inspection under the approved plan; this closeout does not merge those starter PRs
or delete fixtures. See [acceptance.md](acceptance.md) for final disposition.
