from __future__ import annotations


def evaluate_answer(answer: str, contexts: list[str]) -> dict:
    answer_terms = set(answer.lower().split())
    context_terms = set(" ".join(contexts).lower().split())
    overlap = len(answer_terms & context_terms) / max(1, len(answer_terms))
    return {
        "groundedness": round(overlap, 3),
        "has_citations": bool(contexts),
        "fallback": "do not have enough information" in answer.lower(),
    }
