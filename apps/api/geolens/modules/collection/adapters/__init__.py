"""Built-in engine adapters. Importing this package registers them."""

from geolens.modules.collection.adapters import registry
from geolens.modules.collection.adapters.mock import MockAdapter
from geolens.modules.collection.adapters.openai_compatible import SPECS, OpenAICompatibleAdapter


def _register_builtins() -> None:
    registry.register("mock-cn", lambda: MockAdapter("mock-cn", "cn"))
    registry.register("mock-global", lambda: MockAdapter("mock-global", "global"))
    for spec in SPECS:
        registry.register(
            spec.engine_id,
            lambda spec=spec: OpenAICompatibleAdapter(spec),
            enabled=lambda spec=spec: bool(spec.api_key()),
        )


_register_builtins()
