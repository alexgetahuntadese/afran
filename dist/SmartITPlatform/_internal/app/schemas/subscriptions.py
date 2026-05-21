from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import PlanCode, SubscriptionStatus
from app.schemas.common import Timestamped


class SubscriptionRead(Timestamped):
    organization_id: UUID
    plan_code: PlanCode
    status: SubscriptionStatus
    trial_started_at: datetime
    trial_ends_at: datetime | None
    current_period_ends_at: datetime | None
    device_limit: int | None
    feature_flags: dict


class FeatureDecision(BaseModel):
    allowed: bool
    reason: str | None = None
    plan_code: PlanCode
    trial_version_label: str | None = None


class ROIReport(BaseModel):
    organization_id: UUID
    printer_interruptions: int
    offline_devices: int
    network_issues_detected: int
    estimated_downtime_minutes_prevented: int
    headline: str
    upgrade_message: str
