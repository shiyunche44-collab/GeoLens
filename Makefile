# GeoLens — one entrypoint for humans, CI and Claude Code hooks.
# `make check` is the merge gate; `make arch-check` is the fast architecture guard.

API := apps/api
WEB := apps/web
UV := cd $(API) && uv run
QUEUES := default,collect.cn,collect.global,analyze,audit

.PHONY: help setup deps up down migrate api worker web dev demo \
        check lint typecheck arch-check test migrations-check openapi openapi-check \
        web-check arch-report new-module

help: ## Show targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-18s %s\n", $$1, $$2}'

setup: ## Install API + web dependencies
	cd $(API) && uv sync
	cd $(WEB) && pnpm install

deps: ## Start Postgres, Redis, MinIO in Docker
	docker compose up -d postgres redis minio minio-init

up: ## Run the whole stack in Docker (api, worker, web + deps)
	docker compose up -d --build

down: ## Stop the Docker stack
	docker compose down

migrate: ## Apply database migrations
	$(UV) alembic upgrade head

api: ## Run the API with reload
	$(UV) uvicorn geolens.app.main:app --reload --port 8000

worker: ## Run a Celery worker on every queue
	$(UV) celery -A geolens.app.worker worker -Q $(QUEUES) --loglevel=info

web: ## Run the Next.js console
	cd $(WEB) && pnpm dev

demo: ## End-to-end demo against a running API (mock engines)
	$(UV) python scripts/demo.py

# ---------------------------------------------------------------- quality gates

check: lint typecheck arch-check test migrations-check openapi-check web-check ## Everything CI runs

lint: ## Ruff lint + format check
	$(UV) ruff check .
	$(UV) ruff format --check .

typecheck: ## Pyright
	$(UV) pyright

arch-check: ## Import contracts + architecture tests (fast, no DB)
	$(UV) lint-imports
	$(UV) pytest -q tests/architecture

test: ## All Python tests (integration tests skip without Postgres)
	$(UV) pytest -q --cov=geolens --cov-report=term-missing:skip-covered

migrations-check: ## Models and migrations must not drift
	$(UV) alembic upgrade head
	$(UV) alembic check

openapi: ## Regenerate openapi.json and the typed web client
	$(UV) python scripts/export_openapi.py
	cd $(WEB) && pnpm -s gen:api

openapi-check: openapi ## Fail if the committed API contract / web client is stale
	git diff --exit-code -- $(API)/openapi.json $(WEB)/src/lib/api/schema.d.ts

web-check: ## Web lint + typecheck + build
	cd $(WEB) && pnpm -s lint && pnpm -s typecheck && pnpm -s build

# ---------------------------------------------------------------- governance

arch-report: ## Architecture snapshot for milestone reviews
	$(UV) python scripts/arch_report.py

new-module: ## Scaffold a module: make new-module name=alerts
	@test -n "$(name)" || (echo "usage: make new-module name=<snake_case>" && exit 1)
	$(UV) python scripts/new_module.py $(name)
