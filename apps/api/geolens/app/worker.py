"""Celery entrypoint: ``celery -A geolens.app.worker worker -Q collect.cn,...``."""

from geolens.app.bootstrap import load_all
from geolens.core.logging_setup import configure_logging
from geolens.core.queue import celery_app

load_all()
configure_logging()

app = celery_app
