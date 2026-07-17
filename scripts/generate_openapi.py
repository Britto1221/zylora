from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "apps" / "api"))
sys.path.insert(0, str(root / "packages" / "zylora-ai"))

from app.main import app  # noqa: E402

output = root / "packages" / "contracts" / "openapi.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
print(f"Generated {output.relative_to(root)}")
