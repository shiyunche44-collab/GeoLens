# GeoLens API & Workers

Python 3.12 · FastAPI · SQLAlchemy 2 · Celery · PostgreSQL · Redis · S3/MinIO

See the repository root `README.md` and `docs/architecture.md`.

```bash
uv sync                      # install
uv run alembic upgrade head  # migrate
uv run uvicorn geolens.app.main:app --reload
uv run celery -A geolens.app.worker worker -Q default,collect.cn,collect.global,analyze,audit
```
