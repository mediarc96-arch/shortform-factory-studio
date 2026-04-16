#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/docker-exec-as-user.sh <container> <command...>

Runs `docker exec` with the current host UID/GID so commands inside an existing
container do not leave root-owned files in the repo.

Example:
  scripts/docker-exec-as-user.sh my-container bash
EOF
}

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found in PATH." >&2
  exit 1
fi

if [ "$#" -lt 2 ]; then
  usage >&2
  exit 1
fi

container="$1"
shift

tty_flags=(-i)
if [ -t 0 ] && [ -t 1 ]; then
  tty_flags=(-it)
fi

exec docker exec \
  "${tty_flags[@]}" \
  -u "$(id -u):$(id -g)" \
  -e HOME=/tmp/shortform-factory-home \
  -e XDG_CACHE_HOME=/tmp/shortform-factory-home/.cache \
  -e USER="${USER:-user}" \
  -e LOGNAME="${LOGNAME:-${USER:-user}}" \
  "${container}" \
  "$@"
