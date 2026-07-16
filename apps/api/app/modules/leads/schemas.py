from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PublicLeadCreate(BaseModel):
    site_id: UUID
    name: str = Field(min_length=1, max_length=180)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    service: str | None = Field(default=None, max_length=180)
    preferred_contact: str | None = Field(default=None, max_length=30)
    message: str | None = Field(default=None, max_length=5000)
    whatsapp_consent: bool = False
    marketing_consent: bool = False
    source: str = Field(default="website", max_length=80)
    metadata: dict = Field(default_factory=dict)


class LeadUpdate(BaseModel):
    status: str | None = None
    service: str | None = None


class LeadNoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
