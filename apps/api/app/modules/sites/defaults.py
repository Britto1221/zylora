from __future__ import annotations

TEMPLATE_LABELS = {
    "school": "School",
    "coaching": "Coaching centre",
    "clinic": "Clinic",
    "agency": "Agency",
    "general": "Local business",
}


def default_theme() -> dict:
    return {
        "primaryColor": "#111111",
        "secondaryColor": "#3f3f46",
        "accentColor": "#111111",
        "backgroundColor": "#ffffff",
        "surfaceColor": "#f4f4f5",
        "textColor": "#18181b",
        "mutedColor": "#71717a",
        "headingFont": "Inter",
        "bodyFont": "Inter",
        "buttonStyle": "solid",
        "cardStyle": "bordered",
        "radius": 14,
        "sectionSpacing": 80,
        "mode": "light",
    }


def default_content(business_name: str, template_key: str) -> dict:
    industry_nouns = {
        "school": ("Learn with confidence", "Admissions"),
        "coaching": ("Prepare with a clear plan", "Enrol now"),
        "clinic": ("Care centred around you", "Book an appointment"),
        "agency": ("Turn attention into growth", "Start a project"),
        "general": ("A better way to serve your customers", "Contact us"),
    }
    hero, cta = industry_nouns.get(template_key, industry_nouns["general"])
    return {
        "businessName": business_name,
        "navigation": [
            {"label": "Home", "href": "#home"},
            {"label": "Services", "href": "#services"},
            {"label": "About", "href": "#about"},
            {"label": "Contact", "href": "#contact"},
        ],
        "sections": [
            {
                "id": "hero",
                "type": "hero",
                "visible": True,
                "variant": "split",
                "content": {
                    "eyebrow": business_name,
                    "heading": hero,
                    "body": (
                        "Replace this introduction with a clear explanation of the "
                        "business, its value, and who it serves."
                    ),
                    "primaryButton": cta,
                    "primaryHref": "#contact",
                    "secondaryButton": "Explore services",
                    "secondaryHref": "#services",
                    "imageUrl": "",
                    "imageAlt": "",
                },
            },
            {
                "id": "services",
                "type": "services",
                "visible": True,
                "variant": "cards",
                "content": {
                    "eyebrow": "What we offer",
                    "heading": "Services designed around real needs",
                    "body": "Add the business's most important services here.",
                    "items": [
                        {
                            "title": "Service one",
                            "body": "Describe the service and the outcome it provides.",
                        },
                        {
                            "title": "Service two",
                            "body": "Describe the service and the outcome it provides.",
                        },
                        {
                            "title": "Service three",
                            "body": "Describe the service and the outcome it provides.",
                        },
                    ],
                },
            },
            {
                "id": "about",
                "type": "about",
                "visible": True,
                "variant": "editorial",
                "content": {
                    "eyebrow": "About",
                    "heading": f"Why customers choose {business_name}",
                    "body": (
                        "Explain the team's experience, approach, standards, and local credibility."
                    ),
                    "points": ["Clear communication", "Reliable service", "Focused on outcomes"],
                },
            },
            {
                "id": "testimonials",
                "type": "testimonials",
                "visible": True,
                "variant": "quotes",
                "content": {
                    "eyebrow": "Testimonials",
                    "heading": "What customers say",
                    "items": [
                        {
                            "quote": "Add a verified customer testimonial.",
                            "name": "Customer name",
                            "role": "Customer",
                        }
                    ],
                },
            },
            {
                "id": "faq",
                "type": "faq",
                "visible": True,
                "variant": "accordion",
                "content": {
                    "eyebrow": "FAQ",
                    "heading": "Common questions",
                    "items": [
                        {
                            "question": "How do I get started?",
                            "answer": "Contact the business using the form below.",
                        }
                    ],
                },
            },
            {
                "id": "contact",
                "type": "lead-form",
                "visible": True,
                "variant": "panel",
                "content": {
                    "eyebrow": "Contact",
                    "heading": "Tell us what you need",
                    "body": "Submit the form and the business will follow up.",
                    "submitLabel": "Send enquiry",
                    "successMessage": "Thank you. Your enquiry has been received.",
                    "fields": ["name", "email", "phone", "service", "message", "whatsappConsent"],
                },
            },
        ],
        "footer": {
            "summary": f"{business_name} — professional services and responsive support.",
            "email": "",
            "phone": "",
            "address": "",
            "socialLinks": [],
        },
    }


def default_seo(business_name: str) -> dict:
    return {
        "title": business_name,
        "description": f"Learn more about {business_name}, its services, and how to get in touch.",
        "canonicalUrl": "",
        "robots": "index,follow",
        "ogImage": "",
    }
