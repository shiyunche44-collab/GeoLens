---
name: new-module
description: Create a new bounded-context module in the GeoLens backend (e.g. alerts, reports, citations-intel, billing). Use when a feature doesn't belong to any existing module's responsibility.
---

# Add a module (bounded context)

A new module is an **architectural change**. First confirm it doesn't fit an existing
module (see "限界上下文" in `docs/architecture.md`) and that it is in scope for the current
phase (`docs/roadmap.md`). If in doubt, ask the user.

1. `make new-module name=<snake_case>` — scaffolds `geolens/modules/<name>/` (public, api,
   service, repository, models, schemas, README) and registers it in `app/bootstrap.py` and in
   both `.importlinter` module contracts.
2. Write the ADR (`/new-adr`): responsibility, public interface, events consumed/published,
   tables, why it isn't part of an existing module. The CI governance job requires it
   (the scaffold edits `.importlinter`).
3. Implement: tables use `WorkspaceScopedMixin`; cross-module ids are plain `Uuid` columns
   (no FK); other modules are reached only via their `public.py` or events
   (`core.events.subscribe` in your `tasks.py`).
4. Wire the router in `geolens/app/main.py` (`ROUTERS`), then
   `uv run alembic revision --autogenerate -m "<name> tables"` and review the migration.
5. `make openapi` if the API changed; `make check`.
6. Fill in the module `README.md` and add the module to `docs/architecture.md` §3.
