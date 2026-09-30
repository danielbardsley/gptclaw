# Product-owned release contract

Map these facts to existing reviewed project documents and tool schemas; include
their revision. This checklist creates no API, version policy, workflow or role.
Only require facts needed for the selected mode; preparation can report gaps.

| Contract fact | Evidence needed before dependent action |
|---|---|
| Repository/source and version convention | Approved revision, product version rules, release-note scope |
| Candidate | Immutable digest/equivalent ID, build-to-source provenance, required test results |
| Target | Environment and exact pipeline/workflow identity, observed deployed version |
| Dispatch | Fixed input schema, branch/role/environment gates, authorization for artifact plus target |
| Observation | Run ID, request correlation/lost-receipt lookup, poll interval/deadline and terminal meanings |
| Acceptance | Deployed identity source, required health checks and freshness expectations |
| Recovery | Prior artifact, reviewed rollback/roll-forward procedure, data compatibility, backup prerequisites, irreversible-step owner |

A mutable tag may be a label beside a verified digest, never the sole deployment
identity. Approval for one digest/environment does not transfer to another.
Pending protected approval is a waiting state; submitting a run never grants
permission to approve its gate. A denied call is not permission to change roles.

Record contract-specific data safeguards before dispatch. If a migration prevents
rollback, require the reviewed roll-forward path and its prerequisites instead.
Do not substitute an old artifact merely because it exists. Before recovery,
recheck compatibility against actual data transitions and exact authorization.
If a gate or recovery owner decision is missing, prepare the bounded next action.

Provider-success and product-accepted are separate observations. On a lost receipt,
query the documented correlation endpoint. Without a uniquely identified run,
record unknown and stop dispatching. An unrelated concurrent run is not yours to
cancel. On resumption recheck recorded run/target state rather than resubmitting.
Never fetch raw production logs or secrets merely to complete the record.
