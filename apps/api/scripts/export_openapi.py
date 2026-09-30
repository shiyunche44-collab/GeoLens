"""Write the OpenAPI contract to apps/api/openapi.json (consumed by apps/web)."""

import json
import os
from pathlib import Path

os.environ.setdefault("GEOLENS_CELERY_EAGER", "true")

from geolens.app.main import app

out = Path(__file__).resolve().parents[1] / "openapi.json"
out.write_text(
    json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
)
print(f"wrote {out}")
