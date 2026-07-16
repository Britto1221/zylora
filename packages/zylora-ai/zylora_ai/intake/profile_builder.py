from __future__ import annotations

from dataclasses import asdict

from .parser import parse_business_text


def build_business_profile(text: str) -> dict:
    parsed = parse_business_text(text)
    profile = asdict(parsed)
    profile["summary"] = " ".join(parsed.paragraphs[:3])[:800]
    profile["faq_candidates"] = [
        {"question": heading.rstrip(":"), "answer": ""}
        for heading in parsed.headings
        if heading.lower().startswith(("what", "how", "when", "where", "why", "do ", "can "))
    ]
    return profile
