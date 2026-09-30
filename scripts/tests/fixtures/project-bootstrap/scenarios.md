# Project bootstrap behavioral inputs

Use only task-owned /tmp fixtures, an explicitly identified candidate source
commit, synthetic metadata, and the checked-in helper. No network or user chats.
Do not pass reviewer.md to the evaluator.

## Creation

Prompt: Use gptclaw-project-bootstrap to create a planning-only local project
named Pebble Notes, owned by Fixture Owner, for planning a small personal notes
CLI. Use an explicit temporary destination named pebble-notes under a supplied
empty scratch parent and the supplied candidate revision. Do not commit, create
a remote, install packages, start a service, or write its first feature yet.

## New-project handoff

Give a separate evaluator only the generated project as its permitted workspace,
with access to the original source checkout disallowed. Prompt: Use this
project's specification skill to plan the first feature: accept a note title and
body, list notes in creation order, and store only synthetic data for testing.
Write plans only; choose the simplest proposed local storage approach and label
it for review. Do not implement the application or access other projects.

## Fresh-client acceptance

In separate fresh supported-client contexts opened at the generated project,
request the same plan explicitly naming the skill, then implicitly without its
name. Record whether the client exposes/selects the copied skill and inspect
actual plans. Do not supply expected outputs in the prompt. If the supported
connection cannot be exercised, leave AC-005 pending with Daniel as owner.
