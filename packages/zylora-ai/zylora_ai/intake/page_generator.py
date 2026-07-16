from __future__ import annotations


def website_content_suggestions(profile: dict, business_name: str) -> dict:
    paragraphs = profile.get("paragraphs") or []
    headings = profile.get("headings") or []
    return {
        "businessName": business_name,
        "heroHeading": headings[0] if headings else f"Welcome to {business_name}",
        "heroBody": paragraphs[0] if paragraphs else "Add a concise business introduction.",
        "aboutBody": " ".join(paragraphs[1:3]) if len(paragraphs) > 1 else "",
        "email": (profile.get("emails") or [""])[0],
        "phone": (profile.get("phones") or [""])[0],
        "faq": profile.get("faq_candidates") or [],
    }
