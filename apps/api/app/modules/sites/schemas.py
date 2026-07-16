from uuid import UUID

from pydantic import BaseModel


class PublishedSiteRead(BaseModel):
    site_id: UUID
    version_id: UUID
    tenant_id: UUID
    template_key: str
    content: dict
    theme: dict
