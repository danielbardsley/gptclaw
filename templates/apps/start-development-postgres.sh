#!/usr/bin/env bash
# Trusted file-only bootstrap for the exact PostgreSQL 18 image, never project code.
set -Eeuo pipefail
umask 077

: "${PGDATA:?}" "${POSTGRES_USER:?}"
[[ $(id -u) != 0 ]]
[[ "$POSTGRES_USER" =~ ^admin_[a-f0-9]{16}$ ]]
[[ -f /run/secrets/admin.password && -f /run/secrets/admin.passfile ]]
# Refuse raw password environment inputs rather than silently inherit them.
[[ ! ${POSTGRES_PASSWORD+x} && ! ${PGPASSWORD+x} ]]

if ! getent passwd "$(id -u)" >/dev/null; then
  # The pinned Debian image supplies NSS wrapper for arbitrary rootless UIDs.
  export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libnss_wrapper.so
  export NSS_WRAPPER_PASSWD=/tmp/gptclaw-passwd NSS_WRAPPER_GROUP=/tmp/gptclaw-group
  printf 'postgres:x:%s:%s:PostgreSQL:%s:/bin/false\n' "$(id -u)" "$(id -g)" "$PGDATA" > "$NSS_WRAPPER_PASSWD"
  printf 'postgres:x:%s:\n' "$(id -g)" > "$NSS_WRAPPER_GROUP"
fi

if [[ ! -s "$PGDATA/PG_VERSION" ]]; then
  # A partial/unrecognized allocation is retained for recovery, never overwritten.
  [[ -d "$PGDATA" && -z $(ls -A "$PGDATA") ]]
  initdb --pgdata="$PGDATA" --username="$POSTGRES_USER" \
    --pwfile=/run/secrets/admin.password --auth-host=scram-sha-256 --auth-local=scram-sha-256
  # Only the owned internal backend reaches this app-database listener.
  printf '\nhost app all all scram-sha-256\n' >> "$PGDATA/pg_hba.conf"
  pg_ctl --pgdata="$PGDATA" --log=/tmp/gptclaw-init.log --wait --timeout=60 \
    --options='-c listen_addresses=127.0.0.1 -c unix_socket_directories=/tmp -c log_statement=none -c log_min_error_statement=panic' start
  trap 'pg_ctl --pgdata="$PGDATA" --wait --mode=fast stop >/dev/null 2>&1 || true' EXIT
  PGPASSFILE=/run/secrets/admin.passfile psql --no-psqlrc --host=127.0.0.1 \
    --username="$POSTGRES_USER" --dbname=postgres --set=ON_ERROR_STOP=1 \
    --command='CREATE DATABASE app;'
  pg_ctl --pgdata="$PGDATA" --wait --mode=fast stop
  trap - EXIT
fi
[[ $(cat "$PGDATA/PG_VERSION") == 18 ]]
exec postgres -D "$PGDATA" "$@"
