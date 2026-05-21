from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import AlertSeverity, AlertStatus
from app.schemas.common import Timestamped


class AlertCreate(BaseModel):
    organization_id: UUID
    branch_id: UUID | None = None
    device_id: UUID | None = None
    printer_id: UUID | None = None
    severity: AlertSeverity
    title: str
    message: str
    evidence: dict = {}


class AlertRead(Timestamped):
    organization_id: UUID
    branch_id: UUID | None
    device_id: UUID | None
    printer_id: UUID | None
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    acknowledged_by: UUID | None
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    evidence: dict


class AlertAction(BaseModel):
    status: AlertStatus
