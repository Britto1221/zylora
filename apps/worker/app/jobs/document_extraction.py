from app.main import app


@app.task(name="zylora.extract_document")
def extract_document(document_id: str) -> dict:
    # Text documents are processed synchronously by the API in the local build.
    # Production binary/PDF extraction should call the signed-storage document endpoint.
    return {"document_id": document_id, "status": "delegated_to_api"}
