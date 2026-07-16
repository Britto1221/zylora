from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PublicLeadCreate(BaseModel):
    site_id: UUID
    name: str = Field(min_length=1, max_length=180)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    service: str | None = Field(default=None, max_length=180)
    message: str | None = Field(default=None, max_length=5000)
    whatsapp_consent: bool = False


class LeadRead(PublicLeadCreate):
    id: UUID
    tenant_id: UUID
    status: str

    model_config = {"from_attributes": True}
