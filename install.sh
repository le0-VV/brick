#!/usr/bin/env sh
set -eu

if ! command -v git >/dev/null 2>&1; then
  echo "brick install requires git" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$repo_root" ]; then
  echo "brick install must run inside a Git worktree" >&2
  exit 1
fi

cd "$repo_root"

copy_from_checkout() {
  source_dir="$1"
  if [ "$source_dir" = "$repo_root" ]; then
    return
  fi
  mkdir -p .agents/brick/bin .agents/brick/src/brick
  cp "$source_dir/.agents/brick/bin/brick" .agents/brick/bin/brick
  cp "$source_dir/.agents/brick/setup.py" .agents/brick/setup.py
  cp "$source_dir/.agents/brick/pyproject.toml" .agents/brick/pyproject.toml
  cp "$source_dir/.agents/brick/src/brick/__init__.py" .agents/brick/src/brick/__init__.py
  cp "$source_dir/.agents/brick/src/brick/cli.py" .agents/brick/src/brick/cli.py
  cp "$source_dir/.agents/brick/src/brick/conflicts.py" .agents/brick/src/brick/conflicts.py
  cp "$source_dir/.agents/brick/src/brick/index.py" .agents/brick/src/brick/index.py
  cp "$source_dir/.agents/brick/src/brick/memory.py" .agents/brick/src/brick/memory.py
}

fetch_from_base_url() {
  base_url="${BRICK_SOURCE_BASE_URL%/}"
  mkdir -p .agents/brick/bin .agents/brick/src/brick
  curl -fsSL "$base_url/.agents/brick/bin/brick" -o .agents/brick/bin/brick
  curl -fsSL "$base_url/.agents/brick/setup.py" -o .agents/brick/setup.py
  curl -fsSL "$base_url/.agents/brick/pyproject.toml" -o .agents/brick/pyproject.toml
  curl -fsSL "$base_url/.agents/brick/src/brick/__init__.py" -o .agents/brick/src/brick/__init__.py
  curl -fsSL "$base_url/.agents/brick/src/brick/cli.py" -o .agents/brick/src/brick/cli.py
  curl -fsSL "$base_url/.agents/brick/src/brick/conflicts.py" -o .agents/brick/src/brick/conflicts.py
  curl -fsSL "$base_url/.agents/brick/src/brick/index.py" -o .agents/brick/src/brick/index.py
  curl -fsSL "$base_url/.agents/brick/src/brick/memory.py" -o .agents/brick/src/brick/memory.py
}

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)"
if [ -n "$script_dir" ] && [ -f "$script_dir/.agents/brick/bin/brick" ]; then
  copy_from_checkout "$script_dir"
elif [ -n "${BRICK_SOURCE_BASE_URL:-}" ]; then
  fetch_from_base_url
else
  echo "Set BRICK_SOURCE_BASE_URL to the raw URL base for this Brick release." >&2
  exit 2
fi

chmod +x .agents/brick/bin/brick .agents/brick/setup.py
.agents/brick/bin/brick setup "$@"
