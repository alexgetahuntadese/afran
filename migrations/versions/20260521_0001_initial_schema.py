"""initial schema

Revision ID: 20260521_0001
Revises:
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260521_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    device_type = postgresql.ENUM(
        "PC", "LAPTOP", "PRINTER", "ZEBRA_PRINTER", "THERMAL_PRINTER", "ROUTER",
        "SWITCH", "SERVER", "UNKNOWN", name="devicetype"
    )
    device_status = postgresql.ENUM("ONLINE", "OFFLINE", "DEGRADED", name="devicestatus")
    alert_severity = postgresql.ENUM("INFO", "WARNING", "CRITICAL", name="alertseverity")
    alert_status = postgresql.ENUM("OPEN", "ACKNOWLEDGED", "RESOLVED", name="alertstatus")
    plan_code = postgresql.ENUM("TRIAL", "PROFESSIONAL", "ENTERPRISE", name="plancode")
    subscription_status = postgresql.ENUM(
        "ACTIVE", "EXPIRED", "SUSPENDED", "CANCELLED", name="subscriptionstatus"
    )
    remote_status = postgresql.ENUM(
        "REQUESTED", "APPROVED", "ACTIVE", "ENDED", "DENIED", name="remotesessionstatus"
    )
    payment_provider = postgresql.ENUM("CHAPA", "TELEBIRR", "SANTIMPAY", name="paymentprovider")
    for enum in (
        device_type, device_status, alert_severity, alert_status, plan_code,
        subscription_status, remote_status, payment_provider,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("industry", sa.String(80)),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("permissions", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("subnet_cidr", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "name", name="uq_branch_org_name"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="SET NULL")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
    )
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hostname", sa.String(255)),
        sa.Column("ip_address", postgresql.INET, nullable=False),
        sa.Column("mac_address", sa.String(32)),
        sa.Column("vendor", sa.String(160)),
        sa.Column("operating_system", sa.String(160)),
        sa.Column("device_type", device_type, nullable=False),
        sa.Column("status", device_status, nullable=False),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("assigned_user", sa.String(160)),
        sa.Column("department", sa.String(160)),
        sa.Column("floor", sa.String(80)),
        sa.Column("uptime_seconds", sa.Integer),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("branch_id", "ip_address", name="uq_device_branch_ip"),
    )
    op.create_table(
        "printers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("model", sa.String(160)),
        sa.Column("driver_name", sa.String(255)),
        sa.Column("ip_address", postgresql.INET),
        sa.Column("share_name", sa.String(255)),
        sa.Column("department", sa.String(160)),
        sa.Column("floor", sa.String(80)),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("health_score", sa.Integer, nullable=False),
        sa.Column("queue_depth", sa.Integer, nullable=False),
        sa.Column("toner_level", sa.Integer),
        sa.Column("paper_status", sa.String(80)),
        sa.Column("last_checked_at", sa.DateTime(timezone=True)),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="CASCADE")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="SET NULL")),
        sa.Column("printer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("printers.id", ondelete="SET NULL")),
        sa.Column("severity", alert_severity, nullable=False),
        sa.Column("status", alert_status, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("evidence", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("plan_code", plan_code, nullable=False),
        sa.Column("status", subscription_status, nullable=False),
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True)),
        sa.Column("current_period_ends_at", sa.DateTime(timezone=True)),
        sa.Column("device_limit", sa.Integer),
        sa.Column("feature_flags", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "licenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("license_key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("machine_fingerprint", sa.String(255)),
        sa.Column("activated_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "remote_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", remote_status, nullable=False),
        sa.Column("approved_by_user", sa.String(160)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("max_duration_seconds", sa.Integer),
        sa.Column("recording_path", sa.String(500)),
        sa.Column("audit_events", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(160), nullable=False),
        sa.Column("entity_type", sa.String(80)),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("details", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", payment_provider, nullable=False),
        sa.Column("external_reference", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(12), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in (
        "payments", "activity_logs", "remote_sessions", "licenses", "subscriptions",
        "alerts", "printers", "devices", "users", "branches", "roles", "organizations",
    ):
        op.drop_table(table)
    for name in (
        "paymentprovider", "remotesessionstatus", "subscriptionstatus", "plancode",
        "alertstatus", "alertseverity", "devicestatus", "devicetype",
    ):
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
