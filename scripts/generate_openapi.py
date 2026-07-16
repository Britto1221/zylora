from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))

from app.main import app

output = Path("packages/contracts/openapi.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
print(f"Generated {output}")
