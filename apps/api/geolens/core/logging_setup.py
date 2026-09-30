import logging

from geolens.core.config import get_settings


def configure_logging() -> None:
    level = logging.DEBUG if get_settings().env == "dev" else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
