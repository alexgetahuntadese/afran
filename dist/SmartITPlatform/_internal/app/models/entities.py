from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import INET as PG_INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import (
    AlertSeverity,
    AlertStatus,
    DeviceStatus,
    DeviceType,
    PaymentProvider,
    PlanCode,
    RemoteSessionStatus,
    SubscriptionStatus,
)
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

IPAddress = String(64).with_variant(PG_INET(), "postgresql")
JSONDict = JSON().with_variant(JSONB(), "postgresql")


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    industry: Mapped[str | None] = mapped_column(String(80))
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Nairobi")

    branches: Mapped[list["Branch"]] = relationship(back_populates="organization")
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="organization")


class Branch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "branches"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_branch_org_name"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(160))
    location: Mapped[str | None] = mapped_column(String(255))
    subnet_cidr: Mapped[str | None] = mapped_column(String(64))

    organization: Mapped["Organization"] = relationship(back_populates="branches")
    devices: Mapped[list["Device"]] = relationship(back_populates="branch")
    printers: Mapped[list["Printer"]] = relationship(back_populates="branch")


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(80), unique=True)
    permissions: Mapped[dict] = mapped_column(JSONDict, default=dict)


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_user_org_email"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    role_id: Mapped[UUID | None] = mapped_column(ForeignKey("roles.id", ondelete="SET NULL"))
    email: Mapped[str] = mapped_column(String(255), index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization: Mapped["Organization"] = relationship(back_populates="users")
    role: Mapped["Role | None"] = relationship()


class Device(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("branch_id", "ip_address", name="uq_device_branch_ip"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    branch_id: Mapped[UUID] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), index=True)
    hostname: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str] = mapped_column(IPAddress, index=True)
    mac_address: Mapped[str | None] = mapped_column(String(32), index=True)
    vendor: Mapped[str | None] = mapped_column(String(160))
    operating_system: Mapped[str | None] = mapped_column(String(160))
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType), default=DeviceType.UNKNOWN)
    status: Mapped[DeviceStatus] = mapped_column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    assigned_user: Mapped[str | None] = mapped_column(String(160))
    department: Mapped[str | None] = mapped_column(String(160), index=True)
    floor: Mapped[str | None] = mapped_column(String(80))
    uptime_seconds: Mapped[int | None] = mapped_column(Integer)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSONDict, default=dict)

    branch: Mapped["Branch"] = relationship(back_populates="devices")
    printers: Mapped[list["Printer"]] = relationship(back_populates="assigned_device")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="device")


class Printer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "printers"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    branch_id: Mapped[UUID] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), index=True)
    assigned_device_id: Mapped[UUID | None] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255), index=True)
    model: Mapped[str | None] = mapped_column(String(160))
    driver_name: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(IPAddress)
    share_name: Mapped[str | None] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(160))
    floor: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(80), default="unknown")
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    queue_depth: Mapped[int] = mapped_column(Integer, default=0)
    toner_level: Mapped[int | None] = mapped_column(Integer)
    paper_status: Mapped[str | None] = mapped_column(String(80))
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict] = mapped_column(JSONDict, default=dict)

    branch: Mapped["Branch"] = relationship(back_populates="printers")
    assigned_device: Mapped["Device | None"] = relationship(back_populates="printers")


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    branch_id: Mapped[UUID | None] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"))
    device_id: Mapped[UUID | None] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    printer_id: Mapped[UUID | None] = mapped_column(ForeignKey("printers.id", ondelete="SET NULL"))
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.INFO)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.OPEN)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    acknowledged_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence: Mapped[dict] = mapped_column(JSONDict, default=dict)

    device: Mapped["Device | None"] = relationship(back_populates="alerts")


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), unique=True)
    plan_code: Mapped[PlanCode] = mapped_column(Enum(PlanCode), default=PlanCode.TRIAL)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE
    )
    trial_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_period_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    device_limit: Mapped[int | None] = mapped_column(Integer)
    feature_flags: Mapped[dict] = mapped_column(JSONDict, default=dict)

    organization: Mapped["Organization"] = relationship(back_populates="subscription")


class License(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "licenses"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    license_key_hash: Mapped[str] = mapped_column(String(255), unique=True)
    machine_fingerprint: Mapped[str | None] = mapped_column(String(255), index=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RemoteSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "remote_sessions"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    device_id: Mapped[UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"))
    technician_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[RemoteSessionStatus] = mapped_column(
        Enum(RemoteSessionStatus), default=RemoteSessionStatus.REQUESTED
    )
    approved_by_user: Mapped[str | None] = mapped_column(String(160))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    max_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    recording_path: Mapped[str | None] = mapped_column(String(500))
    audit_events: Mapped[dict] = mapped_column(JSONDict, default=dict)


class ActivityLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "activity_logs"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(160), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80))
    entity_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSONDict, default=dict)


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider))
    external_reference: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(12), default="ETB")
    status: Mapped[str] = mapped_column(String(64), default="pending")
    raw_payload: Mapped[dict] = mapped_column(JSONDict, default=dict)
