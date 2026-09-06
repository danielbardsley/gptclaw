# ACCEPTANCE-001: Bootstrap the Remote Development Host

- **Status:** Passed
- **Accepted:** 2026-09-06
- **Specification:** [SPEC-001](./spec.md)
- **Technical design:** [TDD-001](./technical-design.md)
- **Tasks:** [TASKS-001](./tasks.md)
- **Deployed revision:** `ca52f894cd7955969841a0c056d58dfc9a27494d`

## Delivery evidence

| Evidence | Result |
|---|---|
| Pull-request validation | GitHub Actions [run 8](https://github.com/danielbardsley/gptclaw/actions/runs/34040646556) passed for the implementation pull request. |
| Initial pipeline apply | GitHub Actions [run 12](https://github.com/danielbardsley/gptclaw/actions/runs/34041671869) invoked HCP Terraform [run-XjxRAWVmg8vrhsgi](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-XjxRAWVmg8vrhsgi). |
| Dynamic-credential/no-change proof | GitHub Actions [run 13](https://github.com/danielbardsley/gptclaw/actions/runs/34042402349) succeeded after static AWS credentials were removed and reported zero infrastructure changes. |
| Final replacement plan | GitHub Actions [run 31](https://github.com/danielbardsley/gptclaw/actions/runs/34049219829) invoked HCP Terraform [run-pTp7HavLfKneGa1D](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-pTp7HavLfKneGa1D) for revision `ca52f894cd7955969841a0c056d58dfc9a27494d`. |
| Final apply | GitHub Actions [run 32](https://github.com/danielbardsley/gptclaw/actions/runs/34049368432) invoked HCP Terraform [run-UZML5XNdmce21b6T](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-UZML5XNdmce21b6T) successfully for the same revision. |

No local Terraform apply, direct AWS infrastructure mutation, CloudFormation
deployment, saved plan, state file, token, private key, or authentication cache
was used or retained in the repository.

## Sanitized resource inventory

| Resource | Accepted value |
|---|---|
| AWS account and region | `571748613148`, `us-east-1` |
| Availability Zone | `us-east-1a` |
| HCP organization/workspace | `Bardsley` / `gptclaw-dev-host` |
| EC2 instance | `i-02872b301f0d44218`, running |
| Security group | `sg-0dea31b346a469de2`, zero ingress rules |
| Instance profile | `gptclaw-dev-host` |
| Root volume | `vol-04876aac2f3e06baf`, encrypted, delete on termination |
| Project volume | `vol-0f53005235c1e39f3`, encrypted, retained on termination |
| Log group | `/gptclaw/development/forge-dev-01`, 14-day retention |
| SSM | Online, agent `3.3.4793.0` |
| Tailscale/SSH alias | `forge-dev`; exact MagicDNS name recorded in the connection runbook |

Public, private, and Tailscale IP addresses are intentionally omitted from this
record. They are runtime discovery values rather than stable configuration.

## Acceptance criteria

| # | Result | Evidence |
|---:|:---:|---|
| 1 | Pass | HCP workspace exists and Terraform initialized with remote execution. |
| 2 | Pass | State is held in HCP Terraform; repository scans found no local state or saved plan. |
| 3 | Pass | Pull-request run 8 completed the format, validation, test, pin, and secret checks without an apply. |
| 4 | Pass | Final manual plan ran from current `main` in GitHub run 31 and HCP run `run-pTp7HavLfKneGa1D`. |
| 5 | Pass | Exact-confirmation manual apply passed the protected `development` environment in GitHub run 32. |
| 6 | Pass | The EC2 host was created and replaced only by GitHub-triggered HCP Terraform applies. |
| 7 | Pass | Final GitHub plan/apply and HCP records identify revision `ca52f894cd7955969841a0c056d58dfc9a27494d`. |
| 8 | Pass | Read-only AWS verification confirmed account `571748613148`, region `us-east-1`, and AZ `us-east-1a`. |
| 9 | Pass | HCP uses phase-specific AWS OIDC roles; temporary static AWS workspace variables were removed before run 13. |
| 10 | Pass | Repository checks and reviewed logs contain no AWS key, HCP token, Terraform state, saved plan, SSH private key, Tailscale key, or Codex auth cache. |
| 11 | Pass | Security group `sg-0dea31b346a469de2` has an empty ingress list. |
| 12 | Pass | Session Manager access was established and SSM reports the instance online. |
| 13 | Pass | The desktop resolves the full MagicDNS name and reaches alias `forge-dev` through Tailscale. |
| 14 | Pass | `ssh forge-dev` returned hostname `forge-dev-01` and user `forge`. |
| 15 | Pass | The remote login shell resolved `/home/forge/.local/bin/codex`; version `0.153.4`. |
| 16 | Pass | `codex login status` reported ChatGPT authentication; credentials remain outside the repository. |
| 17 | Pass | ChatGPT registered `/srv/forge/projects/gptclaw` as a Git project on remote host `forge-dev`. |
| 18 | Pass | A ChatGPT remote task created `connection-test.md` with hostname and a UTC timestamp. |
| 19 | Pass | That task ran hostname, user, working-directory, UTC-time, and Git commands on the remote host. |
| 20 | Pass | The task displayed the temporary file in Git's untracked-file diff. |
| 21 | Pass | The task removed the file and proved final Git status byte-for-byte equal to the initially clean status. |
| 22 | Pass | Setup and recovery runbooks are committed without secrets. |
| 23 | Pass | GitHub run 13 proved a same-revision, no-variable-change plan produces zero infrastructure changes. |

## Host and remote-task verification

The host verifier passed cloud-init completion, SSM, Tailscale, the persistent
mount, project ownership, bootstrap evidence, SSH, Codex availability, and
repository readability. Bootstrap completion version `3` was recorded at
`2026-09-06T17:46:53Z`.

The ChatGPT remote acceptance task ran in a Codex worktree on `forge-dev-01` as
`forge`. It confirmed the Git common directory was beneath
`/srv/forge/projects/gptclaw/.git`, created the test file with timestamp
`2026-09-06T18:18:35Z`, displayed its two added lines, removed it, and restored
the initially empty Git status. It made no commit, push, or infrastructure
change.

## Operational follow-up

No EBS snapshot existed for the project volume at acceptance time. This does
not fail SPEC-001 because the volume contained only the reproducible repository
clone, but a repository-driven backup workflow is required before storing
non-reproducible project data or performing a future replacement where such
data is at risk.
