from zylora_ai.seo import audit_snapshot


def test_complete_snapshot_scores_higher_than_empty_snapshot() -> None:
    complete = audit_snapshot(
        {
            "businessName": "Northstar Academy",
            "sections": [
                {
                    "id": "hero",
                    "type": "hero",
                    "visible": True,
                    "content": {
                        "heading": "NEET coaching in Chennai",
                        "body": "Focused learning " * 40,
                    },
                },
                {
                    "id": "contact",
                    "type": "lead-form",
                    "visible": True,
                    "content": {"heading": "Contact"},
                },
            ],
        },
        {
            "title": "NEET Coaching in Chennai | Northstar Academy",
            "description": (
                "Prepare for NEET with structured coaching, experienced faculty, "
                "regular testing, and personal guidance in Chennai."
            ),
            "canonicalUrl": "https://northstar.example/",
        },
    )
    empty = audit_snapshot({"sections": []}, {})
    assert complete["score"] > empty["score"]
    assert empty["grade"] == "F"
