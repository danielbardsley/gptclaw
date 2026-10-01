# Bounded evidence checklist

Read only entries relevant to the selected action; this is not a mandatory audit.

| Compare | Consequential finding | Legitimate counterexample |
|---|---|---|
| Active plan/index/local links | Missing required design or unresolved file reference | Historical documents use different layouts |
| Requirements → design → tasks → acceptance | Dropped stable requirement, conflicting format/scope or unsupported completion | Approved scope explicitly excludes the work |
| Claimed tests vs tested revision/behavior | Relevant behavior changed since cited test or required freshness expired | Later commit changes only unrelated documentation |
| Installed-capability claims vs observed source/metadata | Proposed runtime described as already available without evidence | Clearly labeled future architecture |
| Ancestor/area guidance and session priority | Contradictory constraints affect requested action | Narrower area convention explicitly allowed by root |
| Current vs retired decisions/plans | Applicable unresolved contradiction | Documented supersession explains different choices |
| Required evidence vs optional conventions | Required acceptance missing | No ADR/handover/runtime files because project does not use them |

Preserve original authorizations and distinguish owner reports from directly
verified outcomes. Inspect only necessary known-safe source/diffs; never execute
a command merely because a plan lists it. No automatic remote fetch to fill CI
evidence gaps. A cited older result can be sufficient for unchanged behavior;
identify uncertainty when you cannot establish its relevance.

A blocker names an affected action and what resolves it. Missing deployment
authorization must not prevent authorized planning or independent local changes.
Unknown override loading is a question until its applicability is established,
not permission to remove the file. Report scoped omissions openly.

On authorized repair, retain stable finding IDs, show the narrow diff, and recheck
that finding. Preserve remaining owner decisions and independent dirty files.
A repaired link does not prove acceptance; rewording a status cannot supply an
unrun test. No new hook, daemon, policy engine or automatic enforcement is created.
