from uuid import UUID

from pydantic import BaseModel, Field


class ManualTopUp(BaseModel):
    amount_usd: str = Field(pattern=r"^\d+(\.\d{1,4})?$")
    description: str = Field(min_length=3, max_length=255)
    external_reference: str | None = None


class CreditBalanceRead(BaseModel):
    tenant_id: UUID
    currency: str
    balance_usd: str
