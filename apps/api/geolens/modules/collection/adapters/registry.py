from collections.abc import Callable

from geolens.modules.collection.adapters.base import EngineAdapter

AdapterFactory = Callable[[], EngineAdapter]

_factories: dict[str, AdapterFactory] = {}
_enabled: dict[str, Callable[[], bool]] = {}


def register(
    engine_id: str, factory: AdapterFactory, enabled: Callable[[], bool] = lambda: True
) -> None:
    if engine_id in _factories:
        raise ValueError(f"engine {engine_id!r} registered twice")
    _factories[engine_id] = factory
    _enabled[engine_id] = enabled


def unregister(engine_id: str) -> None:
    _factories.pop(engine_id, None)
    _enabled.pop(engine_id, None)


def get(engine_id: str) -> EngineAdapter:
    try:
        return _factories[engine_id]()
    except KeyError as e:
        raise KeyError(f"unknown engine {engine_id!r}") from e


def registered_ids() -> list[str]:
    return sorted(_factories)


def available_ids() -> list[str]:
    """Engines usable right now (e.g. API key configured)."""
    return [eid for eid in registered_ids() if _enabled[eid]()]
