#!/bin/bash
# Governance gate: changing an architecture RULE requires an ADR in the same PR.
#   scripts/check-adr.sh <base-ref>     (CI passes origin/<base>; locally: origin/main)
set -euo pipefail

BASE="${1:-origin/main}"
RULE_FILES=(
  "apps/api/.importlinter"
  "apps/api/tests/architecture/"
  "apps/api/tests/golden/"
  "apps/api/geolens/modules/metrics/definitions.py"
  "apps/api/geolens/core/tenancy.py"
  "apps/api/geolens/core/repository.py"
  "apps/web/eslint.config.mjs"
  ".github/workflows/"
  "Makefile"
)

changed=$(git diff --name-only "$BASE"...HEAD)
touched=()
for f in "${RULE_FILES[@]}"; do
  while IFS= read -r c; do
    [[ -n "$c" && "$c" == "$f"* ]] && touched+=("$c")
  done <<< "$changed"
done

if [ ${#touched[@]} -eq 0 ]; then
  echo "No architecture rule files changed."
  exit 0
fi

if echo "$changed" | grep -qE '^docs/adr/[0-9]{4}-.+\.md$'; then
  echo "Rule files changed and an ADR is included:"
  printf '  %s\n' "${touched[@]}"
  exit 0
fi

echo "::error::Architecture rule files changed without an ADR in docs/adr/:"
printf '  %s\n' "${touched[@]}"
echo "Write an ADR (use the /new-adr skill or copy docs/adr/0000-template.md),"
echo "or, for a purely mechanical change, add the 'no-adr-needed' label to the PR."
exit 1
