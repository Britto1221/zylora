from app.main import app


@app.task(name="zylora.extract_document")
def extract_document(document_id: str) -> dict:
    return {"document_id": document_id, "status": "queued"}
