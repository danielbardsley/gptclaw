# Private platform dashboard

The dashboard source is maintained here as reviewed platform tooling. Its installed
runtime lives separately under `/srv/forge/platform`; project applications continue
under `/srv/forge/projects`. The frontend receives only the collector socket and its
own immutable application assets, never project sources or runtime credentials.

See [SPEC-027](../docs/027-dashboard-project-inventory/spec.md),
[SPEC-028](../docs/028-dashboard-live-service-status/spec.md) and
[SPEC-029](../docs/029-dashboard-project-links/spec.md). The dashboard remains private
through Tailscale Serve. Runtime installation and the exact service/route ownership
procedure are recorded in the dashboard runbook before live rollout.
