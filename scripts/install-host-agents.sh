#!/usr/bin/env bash
set -Eeuo pipefail
command -v python3 >/dev/null || { echo 'prerequisite: python3 is required' >&2; exit 2; }
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$script_dir/lib/host_policy.py" "$@"
