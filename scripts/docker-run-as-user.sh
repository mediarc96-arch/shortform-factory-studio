#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/docker-run-as-user.sh <image> [command...]

Runs `docker run` with the current host UID/GID so bind-mounted repo files do not
become root-owned.

Example:
  scripts/docker-run-as-user.sh python:3.12 bash -lc 'python --version'
EOF
}

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found in PATH." >&2
  exit 1
fi

if [ "$#" -lt 1 ]; then
  usage >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
image="$1"
shift

tty_flags=(-i)
if [ -t 0 ] && [ -t 1 ]; then
  tty_flags=(-it)
fi

exec docker run \
  "${tty_flags[@]}" \
  --rm \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp/shortform-factory-home \
  -e XDG_CACHE_HOME=/tmp/shortform-factory-home/.cache \
  -e USER="${USER:-user}" \
  -e LOGNAME="${LOGNAME:-${USER:-user}}" \
  -v "${repo_root}:/workspace" \
  -w /workspace \
  "${image}" \
  "$@"
