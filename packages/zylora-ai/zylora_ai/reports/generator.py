from __future__ import annotations

import csv
import io
import json


def seo_report_text(audit: dict) -> str:
    lines = [
        f"SEO score: {audit.get('score')}/100 ({audit.get('grade')})",
        audit.get("summary", ""),
        "",
        "Issues",
    ]
    for item in audit.get("issues", []):
        lines.append(f"- [{item.get('severity')}] {item.get('title')}: {item.get('detail')}")
    lines.append("")
    lines.append("Recommendations")
    for item in audit.get("recommendations", []):
        lines.append(f"- {item.get('recommendation')}")
    return "\n".join(lines)


def rows_to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
