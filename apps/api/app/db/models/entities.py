from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import (
    BillingStatus,
    ChangeRequestStatus,
    CreditTransactionType,
    DocumentStatus,
    DomainStatus,
    InvoiceStatus,
    InvoiceType,
    LeadStatus,
    MembershipRole,
    NotificationStatus,
    SeoAuditStatus,
    SiteVersionStatus,
    TenantStatus,
)


def utcnow() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(180))
    legal_name: Mapped[str | None] = mapped_column(String(220))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    industry: Mapped[str] = mapped_column(String(100), default="general")
    owner_name: Mapped[str | None] = mapped_column(String(180))
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(50))
    whatsapp_number: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    monthly_amount_minor: Mapped[int] = mapped_column(Integer, default=0)
    billing_currency: Mapped[str] = mapped_column(String(3), default="USD")
    billing_day: Mapped[int] = mapped_column(Integer, default=1)
    billing_status: Mapped[BillingStatus] = mapped_column(
        Enum(BillingStatus), default=BillingStatus.CURRENT
    )
    operational_status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), default=TenantStatus.ACTIVE
    )
    paused_reason: Mapped[str | None] = mapped_column(Text)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paused_by_user_id: Mapped[UUID | None] = mapped_column(nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TenantNote(Base):
    __tablename__ = "tenant_notes"
    __table_args__ = (Index("ix_tenant_notes_tenant_created", "tenant_id", "created_at"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    author_user_id: Mapped[UUID] = mapped_column(index=True)
    author_email: Mapped[str] = mapped_column(String(320))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TenantMembership(Base, TimestampMixin):
    __tablename__ = "tenant_memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Site(Base, TimestampMixin):
    __tablename__ = "sites"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(180))
    template_key: Mapped[str] = mapped_column(String(80), default="general")
    draft_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    published_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteVersion(Base, TimestampMixin):
    __tablename__ = "site_versions"
    __table_args__ = (
        UniqueConstraint("site_id", "version_number", name="uq_site_version_number"),
        Index("ix_site_versions_tenant_status", "tenant_id", "status"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    site_id: Mapped[UUID] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[SiteVersionStatus] = mapped_column(
        Enum(SiteVersionStatus), default=SiteVersionStatus.DRAFT
    )
    content_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    theme_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    seo_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    validation_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[UUID] = mapped_column()
    approved_by: Mapped[UUID | None] = mapped_column(nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"
    __table_args__ = (Index("ix_leads_tenant_status_created", "tenant_id", "status", "created_at"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    site_id: Mapped[UUID] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(50))
    service: Mapped[str | None] = mapped_column(String(180))
    preferred_contact: Mapped[str | None] = mapped_column(String(30))
    message: Mapped[str | None] = mapped_column(Text)
    whatsapp_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW)
    source: Mapped[str] = mapped_column(String(80), default="website")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class LeadNote(Base):
    __tablename__ = "lead_notes"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    lead_id: Mapped[UUID] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    author_user_id: Mapped[UUID] = mapped_column()
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CreditAccount(Base, TimestampMixin):
    __tablename__ = "credit_accounts"
    __table_args__ = (UniqueConstraint("tenant_id", "currency", name="uq_credit_account_currency"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    balance_micro_usd: Mapped[int] = mapped_column(Integer, default=0)
    reserved_micro_usd: Mapped[int] = mapped_column(Integer, default=0)
    low_balance_threshold_micro_usd: Mapped[int] = mapped_column(Integer, default=5_000_000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CreditReservation(Base, TimestampMixin):
    __tablename__ = "credit_reservations"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_reservation_key"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    credit_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("credit_accounts.id", ondelete="CASCADE"), index=True
    )
    amount_micro_usd: Mapped[int] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reference_type: Mapped[str | None] = mapped_column(String(60))
    reference_id: Mapped[UUID | None] = mapped_column(nullable=True)


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    __table_args__ = (
        Index("ix_credit_transactions_tenant_created", "tenant_id", "created_at"),
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_credit_transaction_idempotency"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    credit_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("credit_accounts.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[CreditTransactionType] = mapped_column(Enum(CreditTransactionType))
    amount_micro_usd: Mapped[int] = mapped_column()
    balance_after_micro_usd: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(String(255))
    external_reference: Mapped[str | None] = mapped_column(String(255))
    idempotency_key: Mapped[str] = mapped_column(String(255))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class NotificationSetting(Base, TimestampMixin):
    __tablename__ = "notification_settings"
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_notification_tenant"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    business_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    visitor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    business_template: Mapped[str] = mapped_column(String(120), default="new_lead")
    visitor_template: Mapped[str] = mapped_column(String(120), default="lead_received")
    business_charge_micro_usd: Mapped[int] = mapped_column(Integer, default=20_000)
    visitor_charge_micro_usd: Mapped[int] = mapped_column(Integer, default=20_000)


class NotificationJob(Base, TimestampMixin):
    __tablename__ = "notification_jobs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_notification_idempotency"),
        Index("ix_notification_status_created", "status", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=True
    )
    recipient_type: Mapped[str] = mapped_column(String(30))
    recipient: Mapped[str] = mapped_column(String(80))
    template_name: Mapped[str] = mapped_column(String(120))
    template_language: Mapped[str] = mapped_column(String(10), default="en")
    template_variables: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING
    )
    charge_micro_usd: Mapped[int] = mapped_column(Integer, default=0)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    provider_status: Mapped[str | None] = mapped_column(String(40))
    provider_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String(255))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Domain(Base, TimestampMixin):
    __tablename__ = "domains"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    site_id: Mapped[UUID] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    hostname: Mapped[str] = mapped_column(String(255), unique=True)
    domain_type: Mapped[str] = mapped_column(String(30), default="custom")
    status: Mapped[DomainStatus] = mapped_column(Enum(DomainStatus), default=DomainStatus.PENDING)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_to_client: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_token: Mapped[str | None] = mapped_column(String(255))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    renewal_price_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("19.00"))
    last_reminder_days: Mapped[int | None] = mapped_column(Integer)


class ApiCredential(Base, TimestampMixin):
    __tablename__ = "api_credentials"
    __table_args__ = (UniqueConstraint("tenant_id", "provider", name="uq_api_credential_provider"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    provider: Mapped[str] = mapped_column(String(50))
    encrypted_secret: Mapped[str] = mapped_column(Text)
    secret_last_four: Mapped[str] = mapped_column(String(4))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("provider", "provider_payment_id", name="uq_provider_payment"),
        UniqueConstraint("provider", "provider_order_id", name="uq_provider_order"),
        Index("ix_payments_tenant_status", "tenant_id", "status"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    provider: Mapped[str] = mapped_column(String(40))
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pack_id: Mapped[str | None] = mapped_column(String(40))
    invoice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"), index=True, nullable=True
    )
    purpose: Mapped[str] = mapped_column(String(40), default="credits")
    charged_amount_minor: Mapped[int] = mapped_column(Integer)
    charged_currency: Mapped[str] = mapped_column(String(3))
    usd_credit_micro_amount: Mapped[int] = mapped_column(Integer, default=0)
    settlement_amount_inr_minor: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), index=True)
    checkout_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("number", name="uq_invoice_number"),
        UniqueConstraint(
            "tenant_id", "invoice_type", "billing_period",
            name="uq_recurring_invoice_period",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    invoice_type: Mapped[InvoiceType] = mapped_column(
        Enum(InvoiceType), default=InvoiceType.ONE_TIME
    )
    billing_period: Mapped[str | None] = mapped_column(String(7), nullable=True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    subtotal_minor: Mapped[int] = mapped_column(Integer)
    tax_minor: Mapped[int] = mapped_column(Integer, default=0)
    total_minor: Mapped[int] = mapped_column(Integer)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    line_items: Mapped[list] = mapped_column(JSON, default=list)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = (UniqueConstraint("provider", "event_id", name="uq_webhook_provider_event"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    event_id: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    payload_hash: Mapped[str] = mapped_column(String(64))
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[str | None] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(80), default="general")
    mime_type: Mapped[str] = mapped_column(String(120), default="text/plain")
    storage_key: Mapped[str | None] = mapped_column(String(500))
    raw_text: Mapped[str | None] = mapped_column(Text)
    extracted_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.UPLOADED
    )
    error_message: Mapped[str | None] = mapped_column(Text)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding_json: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class ChatConversation(Base, TimestampMixin):
    __tablename__ = "chat_conversations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    site_id: Mapped[UUID | None] = mapped_column(index=True)
    visitor_id: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SeoAudit(Base, TimestampMixin):
    __tablename__ = "seo_audits"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    site_id: Mapped[UUID] = mapped_column(index=True)
    version_id: Mapped[UUID | None] = mapped_column(index=True)
    status: Mapped[SeoAuditStatus] = mapped_column(
        Enum(SeoAuditStatus), default=SeoAuditStatus.QUEUED
    )
    score: Mapped[int | None] = mapped_column(Integer)
    grade: Mapped[str | None] = mapped_column(String(2))
    summary: Mapped[str | None] = mapped_column(Text)
    issues_json: Mapped[list] = mapped_column(JSON, default=list)
    recommendations_json: Mapped[list] = mapped_column(JSON, default=list)
    error_message: Mapped[str | None] = mapped_column(Text)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("ix_analytics_tenant_type_created", "tenant_id", "event_type", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    site_id: Mapped[UUID | None] = mapped_column(index=True)
    session_id: Mapped[str | None] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    path: Mapped[str | None] = mapped_column(String(500))
    referrer: Mapped[str | None] = mapped_column(String(500))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ChangeRequest(Base, TimestampMixin):
    __tablename__ = "change_requests"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    category: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL")
    status: Mapped[ChangeRequestStatus] = mapped_column(
        Enum(ChangeRequestStatus), default=ChangeRequestStatus.OPEN
    )
    requested_by: Mapped[UUID | None] = mapped_column(nullable=True)
    quoted_price_minor: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    internal_notes: Mapped[str | None] = mapped_column(Text)
    completion_notes: Mapped[str | None] = mapped_column(Text)


class FeatureFlag(Base, TimestampMixin):
    __tablename__ = "feature_flags"
    __table_args__ = (UniqueConstraint("tenant_id", "key", name="uq_feature_flag"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    key: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    configuration_json: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(index=True, nullable=True)
    actor_user_id: Mapped[UUID] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[UUID | None] = mapped_column(nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ClientInvitation(Base, TimestampMixin):
    __tablename__ = "client_invitations"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_invitation_token_hash"),
        Index("ix_invitation_tenant_status", "tenant_id", "status"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole), default=MembershipRole.CLIENT_ADMIN
    )
    token_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    invited_by: Mapped[UUID] = mapped_column()
    accepted_user_id: Mapped[UUID | None] = mapped_column(nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"
    __table_args__ = (Index("ix_assets_tenant_created", "tenant_id", "created_at"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(index=True)
    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    mime_type: Mapped[str] = mapped_column(String(120))
    detected_mime_type: Mapped[str | None] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(80), default="general")
    alt_text: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    scan_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    scan_provider: Mapped[str | None] = mapped_column(String(40))
    scan_details: Mapped[dict] = mapped_column(JSON, default=dict)
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    public_url: Mapped[str | None] = mapped_column(String(1000))
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
