# GptClaw Platform Feature Catalogue

- **Status:** Directional backlog; not a specification
- **Last updated:** 2026-10-21 (America/New_York)
- **Architecture:** [GptClaw platform architecture](./architecture.md)
- **Mobile delivery track:** [React Native / Expo sequence](./sequence-mobile.md)

## 1. How to use this catalogue

This catalogue records capabilities that may become part of GptClaw. Entries
are intentionally smaller than full specifications and do not contain binding
acceptance criteria or implementation authorization.

When the owner selects a feature or coherent feature slice:

1. Assign the next initiative number.
2. Create `docs/NNN-kebab-case-name/`.
3. Write `spec.md`, then `technical-design.md`, then `tasks.md`.
4. Review consistency with the platform architecture and prior accepted work.
5. Implement only after the owner approves the specification.
6. Add `acceptance.md` when the feature is verified.
7. Whenever a feature's PR has merged and the feature is complete, update this
   catalogue as part of completion: mark it Delivered, link its specification,
   merged PR, and acceptance evidence, and update the catalogue date. Do this
   without waiting for a separate reminder. If implementation is merged but
   acceptance is still pending, record the actual status and remaining checks;
   merging a PR alone does not establish completion.

Feature IDs remain stable even if names, grouping, or delivery order changes.

### Status vocabulary

| Status | Meaning |
|---|---|
| Delivered | Implemented and accepted by a numbered specification. |
| Deployed | Installed in the target environment; final acceptance is still pending. |
| Candidate | Intended direction but not yet specified. |
| Draft | Selected for a numbered specification under review; not approved for implementation. |
| In review | Implemented on a feature branch; review/merge and any remaining acceptance are pending. |
| Implemented | Merged implementation; deployment or final acceptance is pending. |
| Planned | Specification approved; design/tasks under review or awaiting implementation authorization. |
| Optional | Useful capability that should be implemented only when demanded. |
| Deferred | Deliberately postponed until its dependencies or use case exist. |

Priority indicates suggested sequencing, not authorization. When a specification
covers only an initial slice, the row describes that slice and the remaining
backlog separately. A merged draft is still Draft until scope approval is recorded. SPEC-018
implementation was subsequently authorized and merged in PR #40. Its initial
slices are Delivered: live acceptance passed and the provider 1.0.1 closeout
repair/evidence merged in PR #43. Wider row scope remains future work.

The current target is repeatable private application development on the existing
EC2 host. The backlog includes later mobile, dashboard, sharing and production
capabilities; those are not prerequisites for creating the first applications.

## 2. Development foundation

| ID | Feature | Status | Evidence |
|---|---|---|---|
| FND-001 | Pipeline-managed EC2 development host | Delivered | SPEC-001 |
| FND-002 | Encrypted persistent project volume | Delivered | SPEC-001 |
| FND-003 | Tailscale-only SSH with SSM recovery | Delivered | SPEC-001 |
| FND-004 | Remote ChatGPT/Codex project connection | Delivered | SPEC-001 |
| FND-005 | Repository-specific host Git credential | Delivered | SPEC-001 |
| FND-006 | HCP Terraform AWS workload identity | Delivered | SPEC-001 |
| FND-007 | Automatic replacement-host Tailscale enrollment | Deployed | [SPEC-016](../016-tailscale-workload-identity/spec.md): account issuer/trust and host implementation are deployed; recovered PR #35 verification records automatic manual-key-free enrollment and authenticated private SSH through the protected replacement; current receipts/storage and independent SSM are confirmed. Final owner acceptance remains pending. [Evidence](../016-tailscale-workload-identity/acceptance.md). |

## 3. Resilience and host safety

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| RES-001 | Automated EBS snapshots | 1 | Delivered | Daily 03:00 UTC DLM snapshots retaining seven; first natural snapshot completed and post-snapshot plan had no changes on 2026-09-13. Silent failures accepted; no monitoring or notifications. The permitted September 21 retention-expiry follow-up remains unverified in the record; Daniel owns it; restore remains RES-002. [SPEC-002](../002-automated-ebs-snapshots/spec.md); [merged PR #4](https://github.com/danielbardsley/gptclaw/pull/4); [acceptance](../002-automated-ebs-snapshots/acceptance.md). |
| RES-002 | Restore drill | 1 | Candidate | Periodically prove that a recent recovery point can create an inspectable replacement volume without risking the live volume. |
| RES-003 | Backup freshness indicator | 2 | Candidate | Dashboard shows last successful recovery point, age, retention class, and restore-test result. |
| RES-004 | Host replacement rehearsal | 3 | Candidate | Exercise compute replacement, Tailscale re-enrollment, Git credential recreation, and Codex reauthentication. Actual deployment replacements and restored Git/SSM access are evidence of operations; they do not complete a repeatable rehearsal or all replacement acceptance. |
| RES-005 | Host configuration drift detection | 3 | Candidate | Compare declared bootstrap/tool profile with observed packages, units, mounts, and security settings. |
| RES-006 | Disk capacity guardrails | 2 | Candidate | Warn, prune safe caches, and stop risky builds before the persistent volume fills. |
| RES-007 | Platform export | 4 | Optional | Export non-secret manifests, project inventory, and recovery metadata for off-host safekeeping. |

## 4. Agent configuration and consistent delivery

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| AGT-001 | Reviewed host `AGENTS.md` | 2 | Deployed | Policy/installer and first-boot integration merged in [PR #6](https://github.com/danielbardsley/gptclaw/pull/6) and [PR #7](https://github.com/danielbardsley/gptclaw/pull/7). October 9 file inspection found the reviewed policy installed on the replacement host; bytes match its pinned source and metadata. Fresh-task behavior and live rollback acceptance remain pending. [SPEC-003](../003-reviewed-host-agents/spec.md) · [Evidence](../003-reviewed-host-agents/acceptance.md). |
| AGT-002 | Repository `AGENTS.md` template | 2 | Deployed | Template, GptClaw guidance, offline checks and isolated rollback rehearsal merged in [PR #9](https://github.com/danielbardsley/gptclaw/pull/9). Current repository checks and PR #38 CI passed; fresh-task remote acceptance remains pending. [SPEC-004](../004-repository-agents-template/spec.md) · [Evidence](../004-repository-agents-template/acceptance.md). |
| AGT-003 | Nested guidance pattern | 3 | Deployed | [SPEC-005](../005-nested-guidance-pattern/spec.md) approved and implementation authorized on 2026-09-13. Template, five inert examples, infrastructure adoption, and offline checks merged in [PR #11](https://github.com/danielbardsley/gptclaw/pull/11) on 2026-09-13. PR CI run #56 passed; fresh-task remote acceptance remains pending. [Acceptance evidence](../005-nested-guidance-pattern/acceptance.md). |
| AGT-004 | Specification skill | 2 | Deployed | Repository skill, four outlines, and checks merged in [PR #16](https://github.com/danielbardsley/gptclaw/pull/16) as `aed4fe4` on 2026-09-30; owner accepted implementation. Skill available in the repository and observed in the app inventory. Fresh-session behavior checks remain pending before Delivered. [SPEC-006](../006-specification-skill/spec.md) · [Acceptance](../006-specification-skill/acceptance.md). |
| AGT-005 | Project bootstrap skill | 2 | Deployed | Local planning starter, bootstrap skill/helper, and checks merged in [PR #18](https://github.com/danielbardsley/gptclaw/pull/18) as `947a78f` on 2026-09-30; owner approved implementation. Bootstrap skill observed in the app inventory. Fresh-session discovery/use in a generated project remains pending before Delivered. [SPEC-007](../007-project-bootstrap-skill/spec.md) · [Acceptance](../007-project-bootstrap-skill/acceptance.md). |
| AGT-006 | Runtime-operation skill | 3 | Deployed | Skill/resources merged in PR #20 (`033c30b`, 2026-10-01); 17 synthetic scenarios reviewed. SPEC-018 now supplies the reviewed single-web provider and synthetic services; fresh-client live skill acceptance remains pending. [SPEC-008](../008-runtime-operation-skill/spec.md) · [Acceptance](../008-runtime-operation-skill/acceptance.md) · [PR #20](https://github.com/danielbardsley/gptclaw/pull/20). |
| AGT-007 | Release and production-promotion skill | 5 | Deployed | Skill/resources merged in PR #20 (`033c30b`, 2026-10-01); 18 synthetic scenarios reviewed. Existing product contract and isolated non-production rehearsal remain pending. [SPEC-009](../009-release-promotion-skill/spec.md) · [Acceptance](../009-release-promotion-skill/acceptance.md) · [PR #20](https://github.com/danielbardsley/gptclaw/pull/20). |
| AGT-008 | Session handover generator | 3 | Deployed | Skill/outline and isolated Git scenarios merged in PR #20 (`033c30b`, 2026-10-01); producer/consumer evaluation passed after a scoped correction. Client acceptance pending. [SPEC-010](../010-session-handover-generator/spec.md) · [Acceptance](../010-session-handover-generator/acceptance.md) · [PR #20](https://github.com/danielbardsley/gptclaw/pull/20). |
| AGT-009 | Architecture decision records | 3 | Deployed | Template, guide, index, Proposed pilot and 19 lifecycle checks merged in PR #20 (`033c30b`, 2026-10-01). Owner pilot disposition pending. [SPEC-011](../011-architecture-decision-records/spec.md) · [Acceptance](../011-architecture-decision-records/acceptance.md) · [PR #20](https://github.com/danielbardsley/gptclaw/pull/20). |
| AGT-010 | Context validation | 3 | Deployed | Skill/checklist/report and five paired scenarios merged in PR #20 (`033c30b`, 2026-10-01); read-only semantic evaluation passed; two disposable repair checks await explicit authorization after automatic review rejection. Client acceptance pending. [SPEC-012](../012-context-validation/spec.md) · [Acceptance](../012-context-validation/acceptance.md) · [PR #20](https://github.com/danielbardsley/gptclaw/pull/20). |
| AGT-011 | Applicable project skills and working journeys | 2 | Draft | [SPEC-051](../051-project-journey-skills/spec.md): reuse or create planning, runtime, acceptance/handover, Android operation, native preview and journey-verification skills; deliver complete applicable packages through both new-project paths and prioritize a demonstrable principal journey before speculative hardening. Implementation is not yet authorized. |

## 5. Project creation and repository lifecycle

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| PRJ-001 | Versioned project manifest | 2 | Delivered | Single-web-service `.gptclaw/project.yaml`, versioned schema, offline validator, and synthetic example; first feature toward a working private application. Daniel accepted implementation on 2026-09-30 (America/New_York); [PR #22](https://github.com/danielbardsley/gptclaw/pull/22) merged as `aa55583`. All 134 local tests and final PR CI #74 passed. This completes the manifest contract, not live-app acceptance. [SPEC-013](../013-versioned-project-manifest/spec.md) · [Design](../013-versioned-project-manifest/technical-design.md) · [Tasks](../013-versioned-project-manifest/tasks.md) · [Acceptance](../013-versioned-project-manifest/acceptance.md). |
| PRJ-002 | `gptclawctl` CLI | 2 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| PRJ-003 | Template catalogue | 2 | Delivered | [SPEC-021](../021-template-catalogue/spec.md) implements versioned discovery, exact selection and provenance for the existing Next.js web starter in provider 1.3.0. Daniel authorized implementation October 10; 111 focused tests, repository checks and scoped live verification passed. All three final PR-head CI workflows passed. Daniel accepted the reviewed initial slice October 10; [PR #50](https://github.com/danielbardsley/gptclaw/pull/50) merged as `527f04d`. Delivered covers `nextjs@1.0.0` catalogue mechanics; [Evidence](../021-template-catalogue/acceptance.md). API, Python, Expo, static site, CLI and multi-package entries remain later reviewed scope. |
| PRJ-004 | New GitHub repository automation | 3 | Delivered | [SPEC-022](../022-github-repository-automation/spec.md) initial personal-account private-repository workflow in provider 1.4.0 merged in [PR #52](https://github.com/danielbardsley/gptclaw/pull/52) as `869b1b7`. The project owner accepted completion October 10. 41 focused tests, repository checks, all three final-head CI workflows, live repository/initial PR and private app checks passed; the project owner confirmed desktop access. The retained fixture has an explicit owner-approved protection waiver, never claimed as enforced. [Evidence](../022-github-repository-automation/acceptance.md). Token revocation is owner-managed follow-through; PRJ-005 ongoing credentials and broader organization/public/production scope remain separate. |
| PRJ-005 | Repository credential broker | 3 | Delivered | [SPEC-023](../023-repository-credential-broker/spec.md) provider 1.5.2 merged in [PR #54](https://github.com/danielbardsley/gptclaw/pull/54) as `f485190`. The owner-approved All repositories App provides configured private new-repository creation and singleton Git/API credentials after one setup. Live retained recovery/successive creation, native worktree Git/later PRs, scope denial, renewal/revocation/disable/enable, signing-key rotation and two private apps/owner desktop checks passed. 47 broker tests, repository checks, all final-head and push-to-main workflows passed. Earlier narrower failures and public-read/owner-reported retirement limits remain explicit. [Evidence](../023-repository-credential-broker/acceptance.md). Broader organization/public/production scope and fixture PR merges remain separate. |
| PRJ-006 | Branch and worktree policy | 2 | Delivered | [SPEC-032](../032-branch-worktree-policy/spec.md) delivers isolated source-only task checkouts, predictable codex branches, short project locks, scoped Git compatibility and recoverable handoff/cleanup in provider 1.11.0. [PR #74](https://github.com/danielbardsley/gptclaw/pull/74) merged as `9bbdf75`; integrated local checks, four final-head workflows and the owner-authorized Trailboard live exercise passed. Canonical source/data and independent app health were preserved; test checkouts were removed and branches/receipts retained. [Acceptance](../032-branch-worktree-policy/acceptance.md). General task runtime/build/database adapters remain separate scope. |
| PRJ-007 | Project discovery | 3 | Candidate | Dashboard safely discovers valid manifests without executing repository content. |
| PRJ-008 | Project archive and restore | 4 | Candidate | Stop services, retain or export data by policy, archive metadata, and make later restoration predictable. |
| PRJ-009 | Example and seed projects | 3 | Candidate | Golden-path sample applications continuously prove every supported template and routing mode. |
| PRJ-010 | Repository ownership transfer | 5 | Optional | Re-key and move a project without leaking credentials or breaking history. |

## 6. Controlled software installation

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| SYS-001 | Rootless container toolchain | 2 | Deployed | Rootless Podman and supporting configuration are installed on the replacement host. October 9 build/run, bind ownership, DNS/HTTPS, loopback HTTP, non-loopback refusal, crash restart and scoped cleanup passed; the fixture repair merged in [PR #38](https://github.com/danielbardsley/gptclaw/pull/38). Logout/reboot, synthetic-source preservation/rebuild across replacement and final acceptance remain pending. [SPEC-014](../014-rootless-container-toolchain/spec.md) · [Evidence](../014-rootless-container-toolchain/acceptance.md). |
| SYS-002 | Pinned language toolchains | 2 | Delivered | [SPEC-020](../020-pinned-language-toolchains/spec.md) implements initial exact Node/pnpm project selection, immutable profile registry, integrity-verified acquisition, actual-version receipts/reuse, legacy compatibility and consistent lifecycle integration. Reuses the delivered SYS-003 policy. Daniel authorized implementation October 10; local/live checks, 90 focused tests, repository checks and all three configured CI workflows passed in [PR #48](https://github.com/danielbardsley/gptclaw/pull/48). Daniel accepted the reviewed slice October 10; PR #48 merged as `a5e01b2`. Delivered covers the initial Linux amd64 Node 24.21.0/pnpm 12.10.1 scope; Python/uv/Expo and other stacks remain stage-12/later scope. [Design](../020-pinned-language-toolchains/technical-design.md) · [Tasks](../020-pinned-language-toolchains/tasks.md) · [Evidence](../020-pinned-language-toolchains/acceptance.md). |
| SYS-003 | Project dependency policy | 2 | Delivered | [SPEC-019](../019-project-dependency-policy/spec.md) implements policy boundaries and the first typed pnpm dependency adapter: exact changes, frozen restore, disabled install hooks, project/container bounds, lockfile review and recovery. Reuses the delivered SPEC-018 toolchain. Local/live workflow and recovery checks and all three implementation CI checks passed. Daniel accepted the reviewed adapter October 10; [PR #46](https://github.com/danielbardsley/gptclaw/pull/46) merged as `f3cab9f`. Delivered covers the initial public npm/single-root pnpm adapter. Other managers/private sources remain later scope. [Evidence](../019-project-dependency-policy/acceptance.md). [Design](../019-project-dependency-policy/technical-design.md) · [Tasks](../019-project-dependency-policy/tasks.md). |
| SYS-004 | Host tool profile | 2 | Deployed | Profile/bootstrap merged in [PR #25](https://github.com/danielbardsley/gptclaw/pull/25); the replacement host has successful receipts for all 26 components, matching reviewed profile and deployment revision. Full provenance/recovery reconciliation and owner acceptance remain pending. Five approved source-channel exceptions expire November 1. [SPEC-015](../015-host-tool-profile/spec.md) · [Evidence](../015-host-tool-profile/acceptance.md). |
| SYS-005 | Privileged capability broker | 4 | Candidate | Exceptional system changes use a narrow allowlist, owner approval, audit log, and mandatory reconciliation. |
| SYS-006 | Dependency cache management | 3 | Candidate | Share safe package/build caches with quotas while preventing cross-project credential or artifact leakage. |
| SYS-007 | Software bill of materials | 4 | Candidate | Produce SBOMs for images and releases and retain them with build provenance. |

## 7. Parallel project runtime

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| RUN-001 | Rootless project containers | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| RUN-002 | User systemd/Quadlet lifecycle | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| RUN-003 | Port registry | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| RUN-004 | Resource limits | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| RUN-005 | Health contract | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| RUN-006 | Multi-service projects | 3 | Delivered | [SPEC-025](../025-multi-service-projects/spec.md) selects an initial Next.js + Python/FastAPI two-service group with a shared private URL and in-memory notes example; versioned contracts, readiness/order, component preparation, failure recovery and compatibility evidence. Scope approved and implementation authorized October 11; provider 1.7.0 delivers this initial two-container notes slice in [merged PR #58](https://github.com/danielbardsley/gptclaw/pull/58), `c1afac9`. Local/generated/live/client checks and all three reviewed-head CI workflows passed; project owner accepted the slice October 11. The reported hydration warning remains a non-blocking frontend follow-up. [Evidence](../025-multi-service-projects/acceptance.md). Databases, caches, workers and arbitrary graphs remain later scope. |
| RUN-007 | Background jobs and schedulers | 4 | Candidate | Declare recurring or asynchronous workers without unmanaged terminal processes. |
| RUN-008 | Pause, resume, and idle shutdown | 4 | Candidate | Reclaim memory and CPU from inactive projects while preserving data and URLs. |
| RUN-009 | Build queue | 4 | Candidate | Bound concurrent CPU-heavy builds and surface queue state to agents and the dashboard. |
| RUN-010 | Runtime garbage collection | 4 | Candidate | Safely remove orphaned containers, images, caches, ports, and abandoned worktrees. |
| RUN-011 | Development database lifecycle | 3 | Delivered | [SPEC-026](../026-development-databases/spec.md) initial synthetic private web/API/PostgreSQL slice accepted with installed provider 1.8.4: two distinct complete applications, locked private CI, actual browser/owner writes, managed persistence, native recovery/migrations/reset/rotation/interruption, roles/networks and real commit hooks pass. Reviewed implementation PRs #60/#62/#63/#64/#65 are merged; 464 local repository cases and final provider CI pass. Local development credentials remain selected; production/cloud secrets and host-loss recovery are separate. [Evidence](../026-development-databases/acceptance.md). |
| RUN-012 | Synthetic seed-data lifecycle | 4 | Candidate | Load and reset approved non-sensitive datasets consistently. |

## 8. Framework templates

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| TPL-001 | Next.js full-stack template | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| TPL-002 | TypeScript API template | 4 | Delivered | Initial stateless slice under [SPEC-035](../035-typescript-api-template/spec.md) merged in [PR #82](https://github.com/danielbardsley/gptclaw/pull/82): exact Fastify/TypeScript starter, schemas, OpenAPI/bundled docs, health, quality/coverage/container and managed private lifecycle. Final implementation CI passed; two private APIs and managed reload/recovery/test/restart/stop-retention checks passed, and the project owner accepted the result October 15. PostgreSQL/migrations remain explicitly deferred. [Evidence](../035-typescript-api-template/acceptance.md). |
| TPL-003 | Python API/AI template | 4 | Delivered | Initial standalone FastAPI API slice delivered under [SPEC-024](../024-python-fastapi-template/spec.md) and merged in [PR #56](https://github.com/danielbardsley/gptclaw/pull/56): pinned Python/uv execution and dependency policy, exact catalogue release, typed synthetic API/settings, owner-derived standards and quality/security/coverage/CI, private docs/routing and managed lifecycle/repository selection. Local, final-head CI and live checks passed; the project owner confirmed independent docs/echo behavior and accepted the result October 11. [Acceptance](../024-python-fastapi-template/acceptance.md) records the evidence and retained fixtures. AI integrations, databases and multi-service orchestration remain separate scope. |
| TPL-004 | React Native application template (Expo) | 4 | Candidate | Native iOS/Android starter using React Native, Expo Router and TypeScript; pinned compatible SDK/toolchain, accessible native UI, optional typed backend binding, tests and separate environment/build profiles. Web preview is optional; native device acceptance is required. [SPEC-031](../031-expo-project-creation/spec.md) records the delivered creation/quality foundation; full template/device scope remains Candidate. Delivery order: [mobile sequence](sequence-mobile.md). |
| TPL-005 | Static site template | 4 | Delivered | [SPEC-038](../038-static-site-template/spec.md) exact Next.js static-export release, managed private preview/rebuild, accessibility/link checks and asset budgets. Merged in [PR #92](https://github.com/danielbardsley/gptclaw/pull/92); all five final-head CI workflows, private lifecycle/recovery and project-owner UI acceptance passed. Provider 1.17.0; all required criteria and tasks complete. [Evidence](../038-static-site-template/acceptance.md). |
| TPL-006 | CLI/automation template | 5 | Optional | Typed CLI, structured output, tests, packaging, and scheduled execution hooks. |
| TPL-007 | Multi-package product template | 5 | Optional | pnpm workspace with shared contracts and UI packages when one release lifecycle justifies a monorepo. |
| TPL-008 | Shared UI foundation | 4 | Candidate | Accessible components, tokens, themes, forms, error states, and responsive layout conventions. |
| TPL-009 | Authentication starter | 5 | Candidate | Pluggable authentication with secure session defaults and local test identities. |
| TPL-010 | AI-enabled application starter | 5 | Candidate | Server-side OpenAI integration, structured outputs, eval hooks, tracing, limits, and secret-safe configuration. |

## 9. Private networking and previews

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| NET-101 | Private loopback ingress | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| NET-102 | Tailscale Serve manager | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| NET-103 | Base-path compatibility | 3 | Delivered | [SPEC-018](../018-first-private-application/spec.md) initial single-web slice merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40): pinned Next.js starter, rootless lifecycle/limits/ports/health and owned private ingress. Both desktop pages/counters and automatic source updates confirmed; first-app stop/start retained source and kept the second app available. Provider 1.0.1 port-reuse repair and acceptance merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); 32 focused tests, repository checks and all three CI workflows passed. Delivered covers this initial slice; broader row scope remains future work. [Evidence](../018-first-private-application/acceptance.md). |
| NET-104 | Dedicated private service ports | 4 | Candidate | Support applications that cannot operate under a path while keeping access tailnet-only. |
| NET-105 | Funnel exposure manager | 4 | Candidate | Owner-confirmed, time-limited, health-gated public exposure with automatic shutdown and audit. |
| NET-106 | Public exposure authentication | 5 | Candidate | Add application-level identity or share tokens when a Funnel preview is not intentionally anonymous. |
| NET-107 | Exposure policy scanner | 4 | Candidate | Block dashboard, admin, database, log, metric, secret, and non-HTTP endpoints from Funnel. |
| NET-108 | Preview URL registry | 3 | Candidate | Dashboard and task results return stable private URLs and active public URLs with expiry. |
| NET-109 | Tailnet access groups | 4 | Candidate | Express developer/viewer access separately from host administration and Funnel capability. |

## 10. Platform dashboard

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| DSH-001 | Project inventory | 3 | Delivered | [SPEC-027](../027-dashboard-project-inventory/spec.md) implements private inventory, bounded safe discovery, metadata/documentation state and the initial dashboard foundation; local/CI/private/lifecycle/owner acceptance passed; merged in PR #69. |
| DSH-002 | Live service status | 3 | Delivered | [SPEC-028](../028-dashboard-live-service-status/spec.md) defines approved observed health/components, current-instance uptime/restarts, last observed change and explicit freshness over SPEC-027; implemented after inventory; local/CI/private/owner acceptance passed; merged in PR #69. |
| DSH-003 | Private/open links | 3 | Delivered | [SPEC-029](../029-dashboard-project-links/spec.md) defines approved private app/docs/repository links and unavailable/capability-gated logs and preview destinations; implemented after status; local/CI/private/owner acceptance passed; merged in PR #69. Initial app/docs/repository integration is delivered; live logs/preview integration depends on separately accepted prerequisites. |
| DSH-004 | Git status | 3 | Candidate | Show branch, dirty state, ahead/behind, last commit, pull request, and active worktrees. |
| DSH-005 | Resource telemetry | 3 | Candidate | Display host and per-project CPU, memory, disk, network, and process consumption. |
| DSH-006 | Log viewer | 4 | Candidate | Stream and search redacted recent logs with project/component filters. |
| DSH-007 | Build and test status | 4 | Candidate | Show last local checks, GitHub checks, image build, and deployment result. |
| DSH-008 | Backup state | 2 | Candidate | Show snapshot freshness, retention, restore-test status, and recovery warnings. |
| DSH-009 | Constrained controls | 4 | Delivered | [SPEC-037](../037-dashboard-constrained-controls/spec.md) delivers project Start/Stop/Restart/Rebuild and eligible stateless Pause/Resume plus individual service restarts, typed targets, capability gates, confirmations and recoverable results. [PR #86](https://github.com/danielbardsley/gptclaw/pull/86) merged; local/CI/private-runtime/rollback and owner usability acceptance passed. Temporary routing and fixture runtime cleanup are complete. Remote task opening is excluded; DB-group/Metro pause/resume and Metro rebuild remain deferred. |
| DSH-010 | Funnel controls | 4 | Candidate | Request, confirm, time-box, extend, and revoke public exposure with a persistent warning. |
| DSH-011 | Activity and audit timeline | 4 | Candidate | Correlate agent tasks, lifecycle changes, deployments, exposure, alerts, and operator approvals. |
| DSH-012 | Mobile-friendly dashboard | 4 | Candidate | Make status, approvals, logs, and safe controls usable from a phone over Tailscale. |
| DSH-013 | Search and filtering | 4 | Candidate | Find projects by status, stack, owner, tag, repository, health, or exposure. |
| DSH-014 | Read-only degraded mode | 3 | Candidate | Preserve useful diagnosis when the lifecycle manager or a project is unhealthy. |
| DSH-015 | Dashboard visual refinement | 3 | In review | [SPEC-030](../030-dashboard-visual-refinement/spec.md) proposes a compact, readable presentation closer to the project owner's reference, preserving delivered inventory/status/link behavior. Attached HTML is inspected; unsupported demo features are omitted. Implementation/private rollout authorized; local/CI/private browser and rollback checks passed. Owner acceptance and merge pending. |

## 11. Mobile and Expo workflow

The project owner selected mobile delivery planning on October 13. Follow the
[mobile sequence](sequence-mobile.md) to reuse the delivered backend/platform
while extending native contracts. MOB-001 is now selected for
[SPEC-031](../031-expo-project-creation/spec.md); other entries retain their own status. Sequencing does not authorize implementation,
account changes or publication.

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| MOB-001 | Expo project creation | 4 | Delivered | [SPEC-031](../031-expo-project-creation/spec.md) delivers repeatable native source creation through the exact catalogue, mobile manifest/provider, pinned tools/dependencies, quality/bundle checks and private repository workflow. Implementation merged in [PR #73](https://github.com/danielbardsley/gptclaw/pull/73) as `f40a7f3`; local/CI/installed/private rollout and rollback passed. Project owner confirmed dashboard links/runtime messaging and source creation/edit/check acceptance October 13. [Evidence](../031-expo-project-creation/acceptance.md). Metro/device access, backend binding and signed builds remain follow-ups. |
| MOB-002 | Physical-device development | 4 | Delivered | [SPEC-033](../033-private-metro-sessions/spec.md), [merged PR #78](https://github.com/danielbardsley/gptclaw/pull/78) and [acceptance](../033-private-metro-sessions/acceptance.md). Bounded rootless Metro, private transport, exact security/ownership and independent lifecycle/readiness/recovery are merged and installed. Android 11 / Expo Go 57.0.9 physical acceptance and final operator listener cleanup/readback pass. Both temporary runtimes/listeners are absent; source/history, existing HTTPS routes and apps/data are preserved. iOS remains unsupported/follow-up. |
| MOB-003 | Expo Go workflow | 4 | Delivered | [SPEC-034](../034-expo-go-workflow/spec.md), [merged PR #78](https://github.com/danielbardsley/gptclaw/pull/78) and [acceptance](../034-expo-go-workflow/acceptance.md). Read-only eligibility/launch and minimum dashboard Open/copy/local QR are merged and installed. Two-project Android native edit/reload, failure/reconnect/expiry and final owned-listener cleanup pass. Client/SDK/profile freshness is enforced. iOS, signed development builds, account setup and backend CRUD remain separately scoped follow-ups. |
| MOB-004 | Development builds | 4 | Planned | [SPEC-049](../049-mobile-development-builds/spec.md) proposes an Android-first signed development client through bounded EAS cloud builds, reviewed account/signing/upload scope, native compatibility and private Metro/API access. Implementation authorized October 23; provider/contracts, owned build jobs and native starters are in review. Source/EAS security findings and real account/device acceptance remain open. iOS and preview/store distribution remain separate. |
| MOB-005 | Environment profiles | 4 | Candidate | Separate local/development/preview/production API bindings, app identities, builds and update channels. Client configuration is public; server, EAS and signing credentials have scoped storage/handoff and never enter bundles. |
| MOB-006 | EAS Build and Submit | 5 | Candidate | Record reproducible build inputs and external job/artifact provenance, signed development/internal-preview binaries and authorized install access; deliver store testing/submission/release as separately gated slices. |
| MOB-007 | EAS Update policy | 5 | Candidate | Define channels, runtime compatibility, rollout, rollback, and owner approval for updates. |
| MOB-008 | Universal web preview | 4 | Candidate | Export or serve the Expo web target through the same private preview model when appropriate. |
| MOB-009 | Device and release dashboard state | 5 | Candidate | Show distinct Metro/backend/build states, safe launch/install links, freshness, channels and native release versions through reviewed adapters; do not infer a device is online or model installed apps as HTTP containers. |
| MOB-010 | Mobile backend integration | 4 | Delivered | [SPEC-036](../036-mobile-python-backend/spec.md) delivers the selected Android-first Python/FastAPI + PostgreSQL notes integration, merged in [PR #83](https://github.com/danielbardsley/gptclaw/pull/83). Automated/host migration, persistence, rollback and quality evidence plus owner-reported native CRUD/offline/accessibility passes are recorded. The project owner accepted and closed this slice October 21 with explicit remaining manual-evidence waivers in [the closeout](../036-mobile-python-backend/closeout-2026-10-21.md), carried by [PR #91](https://github.com/danielbardsley/gptclaw/pull/91). Trial runtimes are stopped and source/data retained; exact private-listener removal remains an operator follow-up. Broader integration, iOS and signed builds remain separately scoped. |
| MOB-011 | Native application acceptance tests | 4 | Candidate | Pinned native component and device/end-to-end checks for iOS/Android, API CRUD/persistence, app relaunch, offline/reconnect, accessibility and build/update compatibility; record physical-device acceptance separately from web tests. |

## 12. Secrets, data, and security

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| SEC-001 | Project secret registry | 3 | Candidate | Store secrets outside Git and materialize only the values authorized for one project/process. |
| SEC-002 | Secret rotation workflow | 4 | Candidate | Rotate, restart dependants, verify health, and audit without displaying values. |
| SEC-003 | Runtime permission profiles | 3 | Candidate | Express allowed filesystem, network, process, and tool capabilities per project. |
| SEC-004 | Dependency and image scanning | 4 | Candidate | Scan lockfiles, containers, SBOMs, and infrastructure in CI with actionable severity policy. |
| SEC-005 | Repository secret scanning | 2 | Candidate | Expand current pattern checks with pre-commit and CI controls across every generated project. |
| SEC-006 | Audit log | 3 | Candidate | Record actor, request, approval, operation, target, result, and correlation ID without secrets. |
| SEC-007 | Destructive-action controls | 3 | Candidate | Require typed targets, backups where applicable, previews, confirmations, and recoverable defaults. |
| SEC-008 | Production credential isolation | 5 | Candidate | Make production roles usable only by protected GitHub/HCP workflows, never remote project processes. |
| SEC-009 | Tailnet policy as code | 4 | Candidate | Review SSH, Serve, Funnel, device, and project access policy through a controlled source workflow. |
| SEC-010 | Security review workflow | 5 | Candidate | Add threat modeling and targeted review before public exposure or production launch. |

## 13. Quality and developer experience

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| QLT-001 | Standard quality commands | 2 | Implemented | [Specification](../039-standard-quality-commands/spec.md). Exact 1.1.0 successors expose format/lint/typecheck/test/build/security/verify through strict quality.json v1 and pinned containers. Lifecycle manifest meanings and installed providers remain unchanged; source default becomes Next.js 1.1.0. Implementation is merged; remaining acceptance stays recorded. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-002 | Pull-request workflow template | 3 | Implemented | [Specification](../040-pull-request-workflow-template/spec.md). Generated repositories get pinned actions, minimal permissions, caches, tests, scans, and artifacts. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-003 | Dependency automation | 3 | Implemented | [Specification](../041-application-dependency-automation/spec.md). Dependabot or an approved equivalent opens bounded, tested update pull requests for generated applications. New 1.1.0 releases include application/action coverage and cap validation; live bot adoption in existing app repositories remains pending. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-004 | Preview smoke tests | 3 | Implemented | [Specification](../042-private-preview-smoke-tests/spec.md). Source-provider opt-in post-start and bounded source-observer checks verify owned private ingress, assets, health and read-only journeys. Installed-provider rollout and independent private-client acceptance remain pending. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-005 | Accessibility baseline | 4 | Implemented | [Specification](../043-accessibility-baseline/spec.md). Generated web/mobile projects include keyboard, semantics, contrast, and automated accessibility checks. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-006 | Performance budgets | 4 | Implemented | [Specification](../044-performance-budgets/spec.md). Detect unacceptable bundle, response-time, memory, and startup regressions. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-007 | Database migration gates | 4 | Implemented | [Specification](../045-database-migration-gates/spec.md). Test forward migration, backup prerequisites, destructive detection, and rollback/restore strategy. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-008 | Contract and API documentation | 4 | Implemented | [Specification](../046-api-contracts-and-documentation/spec.md). Generate and validate OpenAPI or equivalent contracts where services cross boundaries. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-009 | Golden-template tests | 3 | Implemented | [Specification](../047-golden-template-tests/spec.md). Continuously generate, build, run, route, and destroy sample projects from every supported template. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |
| QLT-010 | Release notes and changelog | 5 | Implemented | [Specification](../048-release-notes-and-changelog/spec.md). Optional; product adoption is not selected. Generate reviewed human-facing release summaries from accepted changes. [Merged PR #95](https://github.com/danielbardsley/gptclaw/pull/95); all task records closed by project-owner direction on 2026-10-21. Remaining acceptance is tracked in the linked initiative. |

## 14. Observability and operations

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| OBS-001 | Structured logging contract | 3 | Candidate | Consistent time, severity, project, component, request, and correlation fields with redaction. |
| OBS-002 | Host and project metrics | 3 | Candidate | Collect enough CPU, memory, disk, network, process, and health data for diagnosis and capacity planning. |
| OBS-003 | Alert routing | 4 | Candidate | Notify on failed health, low disk, stale backup, repeated restarts, and failed deployment. |
| OBS-004 | Trace correlation | 5 | Optional | Add OpenTelemetry-compatible traces where distributed behavior justifies them. |
| OBS-005 | Retention and pruning | 3 | Candidate | Bound journald, CloudWatch, build, image, cache, artifact, and audit growth. |
| OBS-006 | Service-level history | 4 | Candidate | Preserve recent availability and deployment markers for each project. |
| OPS-001 | Cost dashboard | 4 | Candidate | Show current and forecast development/production cost with budget thresholds. |
| OPS-002 | Host schedule | 5 | Optional | Stop the EC2 host during defined idle windows only after reliable remote wake-up exists. |
| OPS-003 | Capacity recommendations | 5 | Optional | Recommend host resizing or project limits from observed demand. |
| OPS-004 | Platform upgrade workflow | 4 | Candidate | Upgrade Ubuntu, Codex, Tailscale, Podman, templates, and schema through reviewed staged changes. |

## 15. Slack and remote collaboration

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| COL-001 | Slack notification adapter | 5 | Candidate | Post task completion, approval requests, failures, health alerts, and exposure expiry notices. |
| COL-002 | Slack command adapter | 5 | Candidate | Authenticated users submit typed project operations without receiving shell access. |
| COL-003 | Slack identity mapping | 5 | Candidate | Map Slack identity to an approved GptClaw role and project scope. |
| COL-004 | Approval workflow | 5 | Candidate | High-impact Slack requests require an explicit owner approval tied to the exact operation. |
| COL-005 | Conversation-to-task bridge | 5 | Candidate | Turn an approved Slack request into a traceable Codex task with repository/project context. |
| COL-006 | Progress summaries | 5 | Candidate | Provide concise, rate-limited updates and links back to the authoritative task and diff. |
| COL-007 | Slack security boundary | 5 | Candidate | Prevent arbitrary prompts, secrets, public channels, replay, and spoofed interactive actions from becoming host commands. |
| COL-008 | Official integration evaluation | 5 | Candidate | Re-evaluate the current Codex Slack integration before building a custom gateway. |

## 16. Production promotion

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| PRD-001 | Production architecture template | 6 | Candidate | Choose managed AWS targets, data, networking, scaling, observability, and recovery from product requirements. |
| PRD-002 | Per-project HCP workspace | 6 | Candidate | Give each production environment isolated state, variables, OIDC roles, approvals, and drift visibility. |
| PRD-003 | Artifact build and registry | 5 | Candidate | Build immutable images/assets once, scan and attest them, then promote the same artifact. |
| PRD-004 | Environment promotion | 6 | Candidate | Move accepted revisions through preview/staging/production with explicit approval and provenance. |
| PRD-005 | Domain and TLS management | 6 | Candidate | Manage DNS, certificates, redirects, and ownership verification through Terraform. |
| PRD-006 | Production secrets | 6 | Candidate | Provision and rotate production secrets without exposing them to development or GitHub logs. |
| PRD-007 | Database deployment | 6 | Candidate | Provision managed PostgreSQL, networking, migrations, backups, monitoring, and recovery controls. |
| PRD-008 | Rollback and roll-forward | 6 | Candidate | Restore a prior artifact or complete a corrective release without ambiguous state. |
| PRD-009 | Production smoke tests | 6 | Candidate | Verify health, critical journeys, observability, and rollback readiness after deployment. |
| PRD-010 | Production incident mode | 6 | Deferred | Provide time-bounded, audited diagnosis without granting the development agent standing production administration. |

## 17. Suggested specification sequence

**Current owner selection (confirmed October 9, 2026, America/New_York):**
Create, run, open and iterate on one private application, then run a second
application independently on the same EC2 host. A second EC2 instance is not
part of this milestone. PRJ-001's manifest is Delivered; rootless tooling and
the host profile are Deployed, with remaining acceptance tracked separately.
Independent SSM recovery and a small container smoke test have passed.

[SPEC-018](../018-first-private-application/spec.md) planning merged in PR #38;
Daniel then authorized implementation. Its initial PRJ-002/TPL-001/RUN-001–005/
NET-101–103 slices are merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40).
Both desktop pages/counters, automatic source updates and first-app source-retaining
stop/start are confirmed. The provider 1.0.1 port-reuse repair and final live evidence
merged in [PR #43](https://github.com/danielbardsley/gptclaw/pull/43); its three CI
workflows passed. This initial private-app slice is Delivered; broader features
remain scoped by their own specifications.
The earlier SPEC-017 acceptance-only draft was closed unmerged; the existing
host acceptance records remain authoritative and their unrun checks stay pending.

Recommended sequence, subject to owner scope review:

1. **Build the first real application:** use the accepted single-web CLI/template
   workflow on this host. Two-app operation, automatic source updates and scoped
   stop/start/source retention are proven; keep measuring actual app feedback
   times as project size grows. No new dashboard or host tool installation is a
   prerequisite.
2. **Make real project delivery routine:** add PRJ-004/005's scoped repository
   creation/credentials when manual setup becomes the next bottleneck; extend
   QLT-001/002/004/009 for standard checks, PR CI and generated-template regression
   tests. Reuse existing branch/guidance conventions before building a larger
   orchestration system. Fit broad manifest commands through reviewed schema work.
3. **Add data and secrets when the first real app needs them:** scope SEC-001,
   RUN-011/012, backups and migration checks together. Until then, manifest v1
   supports ephemeral application data; source retention is a different promise.
4. **Expand only against demonstrated demand:** API/Python/Expo templates,
   dashboards, capacity/cache automation, public previews, Slack and production
   pipelines follow their own reviewed scopes.

Keep operational obligations visible alongside app work: resolve the five host
source-channel exceptions before November 1, record overdue backup retention
follow-up, and complete outstanding agent/host acceptance with appropriate
independent observations. Do not claim these checks passed or launch a new
replacement/reboot merely to tidy catalogue statuses. Restore drills, broader
RES work and full live release-skill acceptance are not prerequisites for the
initial private-app slice; retain existing backups and safeguards.

## 18. Selection checklist

Before asking for a new specification, decide:

- Which feature IDs are in scope.
- What user-visible outcome matters first.
- Which existing project or platform component owns the capability.
- Whether it changes the host, tailnet, GitHub, HCP Terraform, AWS, Expo, or
  production trust boundary.
- Whether it stores data or secrets.
- Whether it creates a public URL.
- Whether it needs a rollback, backup, migration, or destructive-action plan.
- What evidence will prove completion.

The resulting specification may narrow or reject a catalogue idea. The
architecture and catalogue should then be updated so future sessions inherit
the accepted decision.
