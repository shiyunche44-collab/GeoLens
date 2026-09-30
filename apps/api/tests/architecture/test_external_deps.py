"""Third-party SDKs that cost money, touch the network or storage are confined to
known places — so every call is metered, guarded and swappable."""

import grimp
import pytest

# external package -> module prefixes allowed to import it directly
ALLOWED: dict[str, tuple[str, ...]] = {
    "httpx": ("geolens.modules.collection.adapters", "geolens.modules.audit.crawler"),
    "boto3": ("geolens.core.storage",),
    "celery": ("geolens.core.queue",),
    "openai": ("geolens.modules.collection.adapters",),
    "anthropic": ("geolens.modules.collection.adapters",),
    "playwright": ("geolens.modules.collection.adapters", "geolens.modules.audit.crawler"),
    "fastapi": ("geolens.app", "geolens.modules.*.api", "geolens.modules.identity.public"),
    "sqlalchemy": ("geolens.core", "geolens.modules.*.models", "geolens.modules.*.repository"),
}


def _matches(module: str, prefix: str) -> bool:
    parts, pattern = module.split("."), prefix.split(".")
    if len(parts) < len(pattern):
        return False
    return all(p == "*" or p == m for p, m in zip(pattern, parts, strict=False))


@pytest.fixture(scope="module")
def graph() -> grimp.ImportGraph:
    return grimp.build_graph("geolens", include_external_packages=True)


@pytest.mark.parametrize("package", sorted(ALLOWED))
def test_external_package_is_confined(graph: grimp.ImportGraph, package: str) -> None:
    if package not in graph.modules:
        return  # not used anywhere yet
    offenders = sorted(
        importer
        for importer in graph.find_modules_that_directly_import(package)
        if not any(_matches(importer, allowed) for allowed in ALLOWED[package])
    )
    assert not offenders, f"{package} imported outside {ALLOWED[package]}: {offenders}"
