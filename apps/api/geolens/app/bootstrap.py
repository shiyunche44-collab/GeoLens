import importlib

MODULES = ["identity", "projects", "collection", "analysis", "audit", "metrics"]


def load_all() -> None:
    """Import every module's models (ORM metadata) and tasks (Celery + subscriptions)."""
    for name in MODULES:
        for part in ("models", "tasks"):
            try:
                importlib.import_module(f"geolens.modules.{name}.{part}")
            except ModuleNotFoundError as e:
                if e.name != f"geolens.modules.{name}.{part}":
                    raise
