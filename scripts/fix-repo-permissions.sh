#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found in PATH." >&2
  echo "Fallback: sudo chown -R $(id -u):$(id -g) <repo>" >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
uid="$(id -u)"
gid="$(id -g)"
owner_name="$(id -un)"
group_name="$(id -gn)"

docker run --rm \
  -v "${repo_root}:/repo" \
  alpine \
  sh -lc "chown -R ${uid}:${gid} /repo"

leftover_git="$(find "${repo_root}/.git/objects" -maxdepth 2 \( ! -user "${owner_name}" -o ! -group "${group_name}" \) | head -1 || true)"
leftover_renders="$(find "${repo_root}/episodes" -path '*/renders/*' \( ! -user "${owner_name}" -o ! -group "${group_name}" \) | head -1 || true)"

echo "Repo ownership reset to ${uid}:${gid} for ${repo_root}"

if [ -n "${leftover_git}" ] || [ -n "${leftover_renders}" ]; then
  echo "Some paths still have unexpected ownership:" >&2
  [ -n "${leftover_git}" ] && echo "  ${leftover_git}" >&2
  [ -n "${leftover_renders}" ] && echo "  ${leftover_renders}" >&2
  exit 1
fi

echo "Ownership check passed."
