import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))

from app.main import app  # noqa: E402

Path("packages/contracts/openapi.json").write_text(
    json.dumps(app.openapi(), indent=2),
    encoding="utf-8",
)
print("Generated packages/contracts/openapi.json")
