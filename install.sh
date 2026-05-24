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
  mkdir -p .agents/brick/bin .agents/brick/examples/memory-add .agents/brick/examples/memory-files .agents/brick/src/brick
  cp "$source_dir/.agents/brick/bin/brick" .agents/brick/bin/brick
  cp "$source_dir/.agents/brick/AGENT_USAGE.md" .agents/brick/AGENT_USAGE.md
  cp "$source_dir/.agents/brick/setup.py" .agents/brick/setup.py
  cp "$source_dir/.agents/brick/pyproject.toml" .agents/brick/pyproject.toml
  cp "$source_dir/.agents/brick/examples/memory-add/blocked-unsafe.json" .agents/brick/examples/memory-add/blocked-unsafe.json
  cp "$source_dir/.agents/brick/examples/memory-add/command.json" .agents/brick/examples/memory-add/command.json
  cp "$source_dir/.agents/brick/examples/memory-add/decision.json" .agents/brick/examples/memory-add/decision.json
  cp "$source_dir/.agents/brick/examples/memory-add/routine.json" .agents/brick/examples/memory-add/routine.json
  cp "$source_dir/.agents/brick/examples/memory-add/skill.json" .agents/brick/examples/memory-add/skill.json
  cp "$source_dir/.agents/brick/examples/memory-files/command.md" .agents/brick/examples/memory-files/command.md
  cp "$source_dir/.agents/brick/examples/memory-files/decision.md" .agents/brick/examples/memory-files/decision.md
  cp "$source_dir/.agents/brick/examples/memory-files/routine.md" .agents/brick/examples/memory-files/routine.md
  cp "$source_dir/.agents/brick/examples/memory-files/skill.md" .agents/brick/examples/memory-files/skill.md
  cp "$source_dir/.agents/brick/src/brick/__init__.py" .agents/brick/src/brick/__init__.py
  cp "$source_dir/.agents/brick/src/brick/cli.py" .agents/brick/src/brick/cli.py
  cp "$source_dir/.agents/brick/src/brick/conflicts.py" .agents/brick/src/brick/conflicts.py
  cp "$source_dir/.agents/brick/src/brick/index.py" .agents/brick/src/brick/index.py
  cp "$source_dir/.agents/brick/src/brick/memory.py" .agents/brick/src/brick/memory.py
}

fetch_from_base_url() {
  base_url="${BRICK_SOURCE_BASE_URL%/}"
  mkdir -p .agents/brick/bin .agents/brick/examples/memory-add .agents/brick/examples/memory-files .agents/brick/src/brick
  curl -fsSL "$base_url/.agents/brick/bin/brick" -o .agents/brick/bin/brick
  curl -fsSL "$base_url/.agents/brick/AGENT_USAGE.md" -o .agents/brick/AGENT_USAGE.md
  curl -fsSL "$base_url/.agents/brick/setup.py" -o .agents/brick/setup.py
  curl -fsSL "$base_url/.agents/brick/pyproject.toml" -o .agents/brick/pyproject.toml
  curl -fsSL "$base_url/.agents/brick/examples/memory-add/blocked-unsafe.json" -o .agents/brick/examples/memory-add/blocked-unsafe.json
  curl -fsSL "$base_url/.agents/brick/examples/memory-add/command.json" -o .agents/brick/examples/memory-add/command.json
  curl -fsSL "$base_url/.agents/brick/examples/memory-add/decision.json" -o .agents/brick/examples/memory-add/decision.json
  curl -fsSL "$base_url/.agents/brick/examples/memory-add/routine.json" -o .agents/brick/examples/memory-add/routine.json
  curl -fsSL "$base_url/.agents/brick/examples/memory-add/skill.json" -o .agents/brick/examples/memory-add/skill.json
  curl -fsSL "$base_url/.agents/brick/examples/memory-files/command.md" -o .agents/brick/examples/memory-files/command.md
  curl -fsSL "$base_url/.agents/brick/examples/memory-files/decision.md" -o .agents/brick/examples/memory-files/decision.md
  curl -fsSL "$base_url/.agents/brick/examples/memory-files/routine.md" -o .agents/brick/examples/memory-files/routine.md
  curl -fsSL "$base_url/.agents/brick/examples/memory-files/skill.md" -o .agents/brick/examples/memory-files/skill.md
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
