"""Every module follows the same shape and is covered by the import contracts."""

import configparser
from pathlib import Path

import pytest

from geolens.app.bootstrap import MODULES

API_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = API_ROOT / "geolens" / "modules"
ON_DISK = sorted(
    p.name for p in MODULES_DIR.iterdir() if p.is_dir() and (p / "__init__.py").exists()
)


def _contract(name: str) -> configparser.SectionProxy:
    cfg = configparser.ConfigParser()
    cfg.read(API_ROOT / ".importlinter")
    return cfg[f"importlinter:contract:{name}"]


def test_every_module_is_bootstrapped() -> None:
    assert sorted(MODULES) == ON_DISK, "register new modules in geolens/app/bootstrap.py"


@pytest.mark.parametrize("module", ON_DISK)
def test_module_has_public_interface_and_readme(module: str) -> None:
    assert (MODULES_DIR / module / "public.py").exists(), f"{module}: missing public.py"
    assert (MODULES_DIR / module / "README.md").exists(), f"{module}: missing README.md"


@pytest.mark.parametrize(
    "contract,key", [("module-boundaries", "modules"), ("module-layers", "containers")]
)
def test_import_contracts_cover_every_module(contract: str, key: str) -> None:
    listed = {
        line.strip().removeprefix("geolens.modules.")
        for line in _contract(contract)[key].splitlines()
        if line.strip()
    }
    assert listed == set(ON_DISK), f".importlinter [{contract}] must list every module"
