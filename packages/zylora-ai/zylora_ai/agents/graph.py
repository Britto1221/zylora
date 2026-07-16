from __future__ import annotations

from .nodes import format_context
from .prompts import SYSTEM_PROMPT


def build_grounded_prompt(question: str, chunks: list[dict]) -> tuple[str, str]:
    context = format_context(chunks)
    prompt = f"Evidence:\n{context}\n\nQuestion: {question}\n\nAnswer with source references."
    return SYSTEM_PROMPT, prompt
