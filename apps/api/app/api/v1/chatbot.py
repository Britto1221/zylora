from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from zylora_ai.agents.graph import build_grounded_prompt
from zylora_ai.rag.retriever import retrieve

from app.core.security import AuthenticatedUser, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import (
    ChatConversation,
    ChatMessage,
    DocumentChunk,
    FeatureFlag,
    Site,
)
from app.db.session import get_db, set_public_tenant_context
from app.modules.ai_gateway.service import generate_answer

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

FALLBACK = (
    "I do not have enough information to answer that. "
    "Please submit the contact form and the business will contact you."
)


class ChatRequest(BaseModel):
    tenant_id: UUID
    site_id: UUID | None = None
    conversation_id: UUID | None = None
    visitor_id: str | None = Field(default=None, max_length=120)
    question: str = Field(min_length=1, max_length=2000)


def chatbot_enabled(db: Session, tenant_id: UUID) -> bool:
    flag = db.scalar(
        select(FeatureFlag).where(FeatureFlag.tenant_id == tenant_id, FeatureFlag.key == "chatbot")
    )
    return bool(flag and flag.enabled)


@router.post("/public")
def public_chat(payload: ChatRequest, db: Session = Depends(get_db)) -> dict:
    if payload.site_id is None:
        raise HTTPException(status_code=422, detail="site_id is required.")
    site = db.scalar(
        select(Site).where(
            Site.id == payload.site_id,
            Site.tenant_id == payload.tenant_id,
            Site.published_version_id.is_not(None),
        )
    )
    if not site:
        raise HTTPException(status_code=404, detail="Published website not found.")
    set_public_tenant_context(db, payload.tenant_id)
    if not chatbot_enabled(db, payload.tenant_id):
        raise HTTPException(status_code=404, detail="Chatbot is not enabled.")

    conversation = (
        db.get(ChatConversation, payload.conversation_id) if payload.conversation_id else None
    )
    if conversation and conversation.tenant_id != payload.tenant_id:
        raise HTTPException(status_code=403, detail="Conversation does not belong to this website.")
    if not conversation:
        conversation = ChatConversation(
            tenant_id=payload.tenant_id,
            site_id=payload.site_id,
            visitor_id=payload.visitor_id or str(uuid4()),
        )
        db.add(conversation)
        db.flush()

    db.add(
        ChatMessage(
            tenant_id=payload.tenant_id,
            conversation_id=conversation.id,
            role="user",
            content=payload.question,
        )
    )

    records = db.scalars(
        select(DocumentChunk).where(DocumentChunk.tenant_id == payload.tenant_id)
    ).all()
    candidates = [
        {
            "id": str(record.id),
            "content": record.content,
            "embedding": record.embedding_json,
            "source": record.metadata_json.get("document_name", "document"),
        }
        for record in records
    ]
    selected = [
        item for item in retrieve(payload.question, candidates, limit=4) if item["score"] > 0.05
    ]
    if selected:
        system, prompt = build_grounded_prompt(payload.question, selected)
        generated = generate_answer(system=system, prompt=prompt)
        answer = generated or (
            selected[0]["content"][:600]
            + "\n\nThis answer is based on the business documents. "
            + "Please contact the business for confirmation."
        )
        citations = [
            {"source": item["source"], "chunkId": item["id"], "score": round(item["score"], 3)}
            for item in selected
        ]
    else:
        answer = FALLBACK
        citations = []

    message = ChatMessage(
        tenant_id=payload.tenant_id,
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        citations_json=citations,
    )
    db.add(message)
    db.commit()
    return {
        "conversationId": str(conversation.id),
        "messageId": str(message.id),
        "answer": answer,
        "citations": citations,
    }


@router.get("/{tenant_id}/conversations")
def conversations(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(ChatConversation)
        .where(ChatConversation.tenant_id == tenant_id)
        .order_by(ChatConversation.updated_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.get("/{tenant_id}/conversations/{conversation_id}")
def conversation_messages(
    tenant_id: UUID,
    conversation_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    conversation = db.scalar(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.tenant_id == tenant_id,
        )
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at)
    ).all()
    return {
        "conversation": model_dict(conversation),
        "messages": [model_dict(item) for item in messages],
    }
