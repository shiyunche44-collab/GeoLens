#!/bin/bash
# Install dependencies so `make check` (lint, types, arch contracts, tests) works in
# Claude Code on the web. Idempotent; runs synchronously before the session starts.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Python API + workers
(cd "$ROOT/apps/api" && uv sync --quiet)

# Next.js console
if ! command -v pnpm >/dev/null 2>&1; then
  corepack enable >/dev/null 2>&1 || npm install -g pnpm@10 >/dev/null
fi
(cd "$ROOT/apps/web" && pnpm install --prefer-offline --silent)

# Local PostgreSQL for integration tests (skipped gracefully when unavailable)
if command -v pg_ctlcluster >/dev/null 2>&1; then
  cluster=$(pg_lsclusters --no-header 2>/dev/null | awk 'NR==1 {print $1" "$2}')
  if [ -n "$cluster" ]; then
    pg_ctlcluster $cluster start >/dev/null 2>&1 || true
    su postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='geolens'\"" | grep -q 1 \
      || su postgres -c "psql -qc \"CREATE ROLE geolens LOGIN SUPERUSER PASSWORD 'geolens'\""
    for db in geolens geolens_test; do
      su postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='$db'\"" | grep -q 1 \
        || su postgres -c "createdb -O geolens $db"
    done
  fi
fi
