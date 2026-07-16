from __future__ import annotations

from .embedder import cosine_similarity, deterministic_embedding


def retrieve(query: str, chunks: list[dict], *, limit: int = 5) -> list[dict]:
    query_vector = deterministic_embedding(query)
    ranked = []
    for chunk in chunks:
        embedding = chunk.get("embedding") or deterministic_embedding(chunk.get("content", ""))
        ranked.append({**chunk, "score": cosine_similarity(query_vector, embedding)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
