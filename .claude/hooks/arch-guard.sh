#!/bin/bash
# Stop hook: before Claude finishes a turn that touched the API, run the fast
# architecture checks (import contracts + architecture tests, ~2s). On failure,
# exit 2 so the violation is fed back to Claude to fix — instead of reaching CI.
set -uo pipefail

input=$(cat)
# Never block twice in a row (prevents loops if Claude cannot fix it).
if echo "$input" | grep -q '"stop_hook_active": *true'; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
cd "$ROOT" || exit 0
command -v uv >/dev/null 2>&1 || exit 0
[ -d apps/api/.venv ] || exit 0

# Only when API code changed (staged, unstaged or untracked).
if [ -z "$(git status --porcelain -- apps/api 2>/dev/null)" ]; then
  exit 0
fi

if ! out=$(make -s arch-check 2>&1); then
  {
    echo "Architecture guard failed (make arch-check). Fix the violation, or if the rule itself"
    echo "must change, write an ADR first (docs/adr/). Output:"
    echo "$out" | tail -20
  } >&2
  exit 2
fi
exit 0
