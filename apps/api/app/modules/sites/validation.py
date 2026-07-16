from __future__ import annotations

from urllib.parse import urlparse


def validate_snapshot(content: dict, theme: dict, seo: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    business_name = str(content.get("businessName", "")).strip()
    if not business_name:
        errors.append("Business name is required.")

    sections = content.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("At least one website section is required.")
        sections = []

    visible = [section for section in sections if section.get("visible", True)]
    hero_sections = [section for section in visible if section.get("type") == "hero"]
    if len(hero_sections) != 1:
        errors.append("Exactly one visible hero section is required.")

    has_form = any(section.get("type") == "lead-form" for section in visible)
    if not has_form:
        warnings.append("No lead form is visible.")

    for section in visible:
        section_content = section.get("content") or {}
        if section.get("type") == "hero":
            if not str(section_content.get("heading", "")).strip():
                errors.append("The hero heading is required.")
            image_url = str(section_content.get("imageUrl", "")).strip()
            image_alt = str(section_content.get("imageAlt", "")).strip()
            if image_url and not image_alt:
                warnings.append("Hero image alt text is missing.")

    title = str(seo.get("title", "")).strip()
    description = str(seo.get("description", "")).strip()
    if not title:
        errors.append("SEO title is required.")
    elif len(title) > 65:
        warnings.append("SEO title exceeds 65 characters.")
    if not description:
        errors.append("Meta description is required.")
    elif len(description) > 170:
        warnings.append("Meta description exceeds 170 characters.")

    canonical = str(seo.get("canonicalUrl", "")).strip()
    if canonical:
        parsed = urlparse(canonical)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("Canonical URL must be an absolute HTTP(S) URL.")

    required_theme = ["primaryColor", "backgroundColor", "textColor", "headingFont", "bodyFont"]
    for key in required_theme:
        if not theme.get(key):
            errors.append(f"Theme value '{key}' is required.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "businessName": bool(business_name),
            "sectionCount": len(visible),
            "leadForm": has_form,
            "singleHero": len(hero_sections) == 1,
            "seoTitle": bool(title),
            "metaDescription": bool(description),
        },
    }
