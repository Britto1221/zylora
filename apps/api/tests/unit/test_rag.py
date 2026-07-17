from zylora_ai.rag.chunker import chunk_text
from zylora_ai.rag.embedder import deterministic_embedding
from zylora_ai.rag.retriever import retrieve


def test_chunking_and_retrieval_are_deterministic() -> None:
    chunks = chunk_text(
        "Admissions open for science and mathematics coaching. " * 80, size=200, overlap=30
    )
    assert len(chunks) > 1
    records = [
        {"id": str(index), "content": content, "embedding": deterministic_embedding(content)}
        for index, content in enumerate(chunks)
    ]
    first = retrieve("science coaching admissions", records)
    second = retrieve("science coaching admissions", records)
    assert first == second
    assert first[0]["score"] > 0
