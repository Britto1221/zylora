from __future__ import annotations


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[Source {index + 1}: {chunk.get('source', 'document')}]\n{chunk.get('content', '')}"
        for index, chunk in enumerate(chunks)
    )
