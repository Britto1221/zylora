from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedBusinessContent:
    headings: list[str]
    paragraphs: list[str]
    emails: list[str]
    phones: list[str]
    urls: list[str]


def parse_business_text(text: str) -> ParsedBusinessContent:
    clean = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    lines = clean.splitlines()
    headings = [
        line for line in lines
        if len(line) <= 80 and (line.isupper() or line.endswith(":") or len(line.split()) <= 6)
    ][:30]
    paragraphs = [line for line in lines if line not in headings and len(line) >= 30][:100]
    emails = sorted(set(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", clean)))
    phones = sorted(set(re.findall(r"(?:\+?\d[\d\s()-]{7,}\d)", clean)))
    urls = sorted(set(re.findall(r"https?://[^\s)>\]]+", clean)))
    return ParsedBusinessContent(
        headings=headings,
        paragraphs=paragraphs,
        emails=emails,
        phones=phones,
        urls=urls,
    )
