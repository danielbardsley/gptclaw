#!/usr/bin/env bash
set -u

failures=0

check() {
  local name=$1
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'PASS %s\n' "$name"
  else
    printf 'FAIL %s\n' "$name"
    failures=$((failures + 1))
  fi
}

check_any_service() {
  local name=$1
  shift
  local service
  for service in "$@"; do
    if systemctl is-active --quiet "$service"; then
      printf 'PASS %s (%s)\n' "$name" "$service"
      return 0
    fi
  done
  printf 'FAIL %s\n' "$name"
  failures=$((failures + 1))
}

run_as_forge() {
  if [ "$(id -un)" = "forge" ]; then
    "$@"
  else
    sudo -iu forge "$@"
  fi
}

printf 'GptClaw development host verification\n'
printf 'UTC %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'Host %s\n' "$(hostname)"

check "cloud-init complete" cloud-init status --wait
check_any_service "SSM agent active" \
  amazon-ssm-agent.service \
  snap.amazon-ssm-agent.amazon-ssm-agent.service
check "Tailscale daemon active" systemctl is-active --quiet tailscaled.service
check "Tailscale connected" tailscale status
check "project volume mounted" mountpoint -q /srv/forge
check "project directory ownership" bash -c '[ "$(stat -c "%U:%G:%a" /srv/forge/projects)" = "forge:forge:750" ]'
check "bootstrap evidence present" test -r /var/lib/gptclaw/bootstrap-complete.json
check "SSH service active" systemctl is-active --quiet ssh.service
if [ "$(id -u)" -eq 0 ]; then
  check "SSH configuration valid" sshd -t
fi
check "Codex in forge login PATH" run_as_forge sh -lc 'command -v codex'
check "Codex executable" run_as_forge sh -lc 'codex --version'

if [ -d /srv/forge/projects/gptclaw/.git ]; then
  check "GptClaw repository readable" run_as_forge git -C /srv/forge/projects/gptclaw status --short --branch
else
  printf 'SKIP GptClaw repository not cloned yet\n'
fi

if [ -r /var/lib/gptclaw/bootstrap-complete.json ]; then
  jq '{bootstrap_version, completed_at, status, components}' /var/lib/gptclaw/bootstrap-complete.json
fi

if [ "$failures" -ne 0 ]; then
  printf '%s verification check(s) failed\n' "$failures" >&2
  exit 1
fi

printf 'All applicable verification checks passed\n'
