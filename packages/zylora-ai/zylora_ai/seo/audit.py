from __future__ import annotations

from urllib.parse import urlparse


def audit_snapshot(content: dict, seo: dict) -> dict:
    issues: list[dict] = []
    recommendations: list[dict] = []
    score = 100

    def issue(code: str, severity: str, title: str, detail: str, penalty: int, recommendation: str):
        nonlocal score
        score -= penalty
        item = {"code": code, "severity": severity, "title": title, "detail": detail}
        issues.append(item)
        recommendations.append({**item, "recommendation": recommendation})

    title = str(seo.get("title", "")).strip()
    description = str(seo.get("description", "")).strip()
    if not title:
        issue("missing_title", "critical", "Missing page title", "No SEO title is configured.", 18, "Add a specific title containing the business and primary service.")
    elif len(title) > 65:
        issue("long_title", "warning", "Title is too long", f"The title contains {len(title)} characters.", 5, "Shorten the title to about 50–60 characters.")
    if not description:
        issue("missing_description", "critical", "Missing meta description", "No meta description is configured.", 14, "Write a clear 140–160 character description.")
    elif not 110 <= len(description) <= 170:
        issue("description_length", "warning", "Meta description length", f"The description contains {len(description)} characters.", 4, "Keep the description between roughly 110 and 170 characters.")

    sections = [section for section in content.get("sections", []) if section.get("visible", True)]
    heroes = [section for section in sections if section.get("type") == "hero"]
    if len(heroes) != 1:
        issue("hero_h1", "critical", "Invalid primary heading structure", f"Found {len(heroes)} visible hero sections.", 15, "Keep one visible hero section with one clear primary heading.")

    word_count = len(" ".join(str(section.get("content", {})) for section in sections).split())
    if word_count < 180:
        issue("thin_content", "warning", "Thin page content", f"Only about {word_count} words were detected.", 10, "Add original service, trust, FAQ, and local context.")

    missing_alt = 0
    for section in sections:
        block = section.get("content") or {}
        if block.get("imageUrl") and not str(block.get("imageAlt", "")).strip():
            missing_alt += 1
    if missing_alt:
        issue("missing_alt", "warning", "Missing image alt text", f"{missing_alt} image(s) lack alt text.", 3 * missing_alt, "Write useful alt text for meaningful images.")

    if not any(section.get("type") == "lead-form" for section in sections):
        issue("missing_conversion", "info", "No lead form", "The page has no visible lead form.", 6, "Add a focused enquiry form.")

    canonical = str(seo.get("canonicalUrl", "")).strip()
    if canonical and not urlparse(canonical).netloc:
        issue("invalid_canonical", "warning", "Invalid canonical URL", "The canonical URL is not absolute.", 5, "Use a complete HTTPS canonical URL.")

    score = max(0, min(100, score))
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
    return {
        "score": score,
        "grade": grade,
        "summary": f"The website scored {score}/100 ({grade}). {len(issues)} issue(s) require review.",
        "issues": issues,
        "recommendations": recommendations,
    }
