from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import RemoteSessionStatus
from app.schemas.common import Timestamped


class RemoteSessionCreate(BaseModel):
    device_id: UUID


class RemoteSessionRead(Timestamped):
    organization_id: UUID
    device_id: UUID
    technician_id: UUID
    status: RemoteSessionStatus
    approved_by_user: str | None
    started_at: datetime | None
    ended_at: datetime | None
    max_duration_seconds: int | None
    recording_path: str | None
    audit_events: dict
