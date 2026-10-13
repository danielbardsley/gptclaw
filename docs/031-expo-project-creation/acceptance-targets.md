# SPEC-031 proposed private acceptance targets

- **Status:** Prepared proposal; exact-name authorization pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)

| Target | Source root | Planned private repository | Public development identities |
|---|---|---|---|
| mob001-accept-one | /srv/forge/projects/mob001-accept-one | https://github.com/danielbardsley/mob001-accept-one | iOS dev.gptclaw.mob001-accept-one; Android dev.gptclaw.mob001_accept_one |
| mob001-accept-two | /srv/forge/projects/mob001-accept-two | https://github.com/danielbardsley/mob001-accept-two | iOS dev.gptclaw.mob001-accept-two; Android dev.gptclaw.mob001_accept_two |

Use the exact frozen expo-react-native@1.0.0 through the source and refreshed owned
provider. Create private repositories and initial review branches/PRs with the
existing activated App broker. The existing private-dev protection waiver policy
remains explicit; no enforced branch protection is claimed.

The current workflow publication allowlist contains only Shelfmark and Trailboard.
Propose broker profile schema 4 with a maximum of four explicitly selected names:
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
fixture names. This proposal supplies that concrete scope. No live target has been
created and no workflow policy has been changed yet.

## Additional supporting-scope approval needed

The existing schema-3 policy has a hard two-name limit. A schema-4 four-name
extension is needed to preserve both existing names while publishing the two
mobile workflows. Existing App/installation grants and singleton token scopes
remain unchanged. Older providers cannot interpret profile 4; retain the capable
snapshot or restore the previous reviewed policy through its typed interface
before rollback.

Two existing bindings refer to source archived by the earlier authorized cleanup.
The helper update currently requires every source root to exist. Propose preserving
absent-root bindings/helpers without changing their path or reading archived Git
config, while keeping incomplete helper-upgrade journals blocking. Refresh only
existing owned live helper paths. Restored source requires a compatible reviewed
helper update before credential use. No binding, repository or source is deleted.

Automatic approval review rejected the earlier proposed 64-name schema and archived
helper change because that persistent security-scope expansion lacked exact owner
authorization. Nothing from that rejected command ran. This smaller four-name
proposal is for explicit owner approval before coding or activation; it is not a
workaround or a claim that approval already exists. Source-only acceptance and
other authorized checks continue independently.
