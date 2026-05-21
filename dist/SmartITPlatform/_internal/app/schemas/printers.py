from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import Timestamped


class PrinterRead(Timestamped):
    organization_id: UUID
    branch_id: UUID
    assigned_device_id: UUID | None
    name: str
    model: str | None
    driver_name: str | None
    ip_address: str | None
    share_name: str | None
    department: str | None
    floor: str | None
    status: str
    health_score: int
    queue_depth: int
    toner_level: int | None
    paper_status: str | None
    last_checked_at: datetime | None
    metadata_json: dict


class PrinterActionResponse(BaseModel):
    printer_id: UUID | None = None
    action: str
    ok: bool
    message: str
    details: dict = {}
