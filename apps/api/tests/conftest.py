import os
import tempfile

# Configure BEFORE geolens is imported: settings and the Celery app read env at import.
os.environ.setdefault("GEOLENS_ENV", "test")
os.environ.setdefault(
    "GEOLENS_DATABASE_URL", "postgresql+psycopg://geolens:geolens@localhost:5432/geolens_test"
)
os.environ["GEOLENS_CELERY_EAGER"] = "true"
os.environ["GEOLENS_STORAGE_BACKEND"] = "local"
os.environ["GEOLENS_STORAGE_LOCAL_DIR"] = tempfile.mkdtemp(prefix="geolens-raw-")
os.environ["GEOLENS_AUDIT_ALLOW_PRIVATE_HOSTS"] = "true"

from geolens.app.bootstrap import load_all

load_all()
