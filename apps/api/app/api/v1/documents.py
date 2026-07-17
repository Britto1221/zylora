from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from zylora_ai.intake.profile_builder import build_business_profile
from zylora_ai.rag.chunker import chunk_text
from zylora_ai.rag.embedder import deterministic_embedding

from app.core.security import AuthenticatedUser, require_tenant_access, require_tenant_admin
from app.core.serialization import model_dict
from app.db.models.entities import Asset, Document, DocumentChunk
from app.db.models.enums import DocumentStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.documents.service import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])


class TextDocumentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(default="general", max_length=80)
    text: str = Field(min_length=1, max_length=2_000_000)


@router.get("/{tenant_id}")
def list_documents(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    documents = db.scalars(
        select(Document).where(Document.tenant_id == tenant_id).order_by(Document.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in documents]}


@router.post("/{tenant_id}", status_code=status.HTTP_201_CREATED)
def create_text_document(
    tenant_id: UUID,
    payload: TextDocumentCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    document = Document(
        tenant_id=tenant_id,
        name=payload.name,
        category=payload.category,
        mime_type="text/plain",
        raw_text=payload.text,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.flush()

    try:
        profile = build_business_profile(payload.text)
        document.extracted_json = profile
        chunks = chunk_text(payload.text)
        for position, content in enumerate(chunks):
            db.add(
                DocumentChunk(
                    tenant_id=tenant_id,
                    document_id=document.id,
                    position=position,
                    content=content,
                    embedding_json=deterministic_embedding(content),
                    metadata_json={"document_name": document.name, "category": document.category},
                )
            )
        document.status = DocumentStatus.READY
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)

    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="document",
        entity_id=document.id,
        action="document.created",
        payload={"name": document.name, "status": document.status.value},
    )
    db.commit()
    return model_dict(document)


@router.get("/{tenant_id}/{document_id}")
def get_document(
    tenant_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.tenant_id == tenant_id)
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.position)
    ).all()
    return {"document": model_dict(document), "chunks": [model_dict(chunk) for chunk in chunks]}


@router.delete("/{tenant_id}/{document_id}", status_code=204)
def delete_document(
    tenant_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
):
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.tenant_id == tenant_id)
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="document",
        entity_id=document.id,
        action="document.deleted",
        payload={"name": document.name},
    )
    db.delete(document)
    db.commit()


@router.post("/{tenant_id}/from-asset/{asset_id}", status_code=status.HTTP_201_CREATED)
def create_document_from_asset(
    tenant_id: UUID,
    asset_id: UUID,
    category: str = "general",
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    asset = db.scalar(
        select(Asset).where(
            Asset.id == asset_id,
            Asset.tenant_id == tenant_id,
            Asset.status == "READY",
        )
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Ready asset not found.")
    document = Document(
        tenant_id=tenant_id,
        name=asset.filename,
        category=category,
        mime_type=asset.mime_type,
        storage_key=asset.storage_key,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.flush()
    try:
        text = extract_text(asset)
        if not text.strip():
            raise ValueError("No readable text was extracted.")
        document.raw_text = text
        document.extracted_json = build_business_profile(text)
        for position, content in enumerate(chunk_text(text)):
            db.add(
                DocumentChunk(
                    tenant_id=tenant_id,
                    document_id=document.id,
                    position=position,
                    content=content,
                    embedding_json=deterministic_embedding(content),
                    metadata_json={
                        "document_name": document.name,
                        "category": document.category,
                        "asset_id": str(asset.id),
                    },
                )
            )
        document.status = DocumentStatus.READY
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="document",
        entity_id=document.id,
        action="document.asset_extracted",
        payload={"asset_id": str(asset.id), "status": document.status.value},
    )
    db.commit()
    return model_dict(document)
