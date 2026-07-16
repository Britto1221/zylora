from uuid import UUID

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class TenantRead(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool

    model_config = {"from_attributes": True}
