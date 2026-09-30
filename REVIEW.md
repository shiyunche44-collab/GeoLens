# Review guide (for human reviewers and review bots)

Automated gates already cover: import contracts, tenant columns, cross-module FKs,
external SDK confinement, golden metrics/analysis, OpenAPI drift, migrations drift.
Reviews should focus on what machines can't judge:

## Blocking

- **Boundary leaks the linters can't see**: ORM objects or SQLAlchemy sessions returned
  through `public.py` (must be DTOs); business logic in `api.py`/`tasks.py` instead of `service.py`.
- **Tenant isolation**: raw `select(...)` / `session.execute` on a workspace-scoped table
  that bypasses `WorkspaceRepository` filtering; tasks enqueued without `workspace_id`.
- **Idempotency**: Celery tasks must tolerate redelivery (check state before side effects);
  collection must not create a second `Response` for the same `QueryTask`.
- **Raw snapshot first**: a new adapter/collector that parses without persisting the raw payload.
- **Unmetered cost**: a new external LLM/SERP/crawl call without `record_usage`.
- **Security**: user-supplied URLs fetched without `assert_public_http_url` (SSRF);
  secrets logged or stored unencrypted; API keys in fixtures.
- **Metric semantics**: a formula change outside `metrics/definitions.py`, or golden
  files edited without an ADR explaining the new definition.
- **Scope creep**: features from a later roadmap phase (docs/roadmap.md "明确不做").

## Non-blocking (nit)

- Module README out of date; naming; missing docstring on a public function.
