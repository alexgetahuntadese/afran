from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import DeviceStatus, DeviceType
from app.schemas.common import Timestamped


class DeviceCreate(BaseModel):
    organization_id: UUID
    branch_id: UUID
    ip_address: str
    hostname: str | None = None
    mac_address: str | None = None
    vendor: str | None = None
    operating_system: str | None = None
    device_type: DeviceType = DeviceType.UNKNOWN
    status: DeviceStatus = DeviceStatus.OFFLINE
    latency_ms: int | None = None
    department: str | None = None
    floor: str | None = None


class DeviceUpdate(BaseModel):
    hostname: str | None = None
    mac_address: str | None = None
    vendor: str | None = None
    operating_system: str | None = None
    device_type: DeviceType | None = None
    status: DeviceStatus | None = None
    latency_ms: int | None = None
    assigned_user: str | None = None
    department: str | None = None
    floor: str | None = None
    uptime_seconds: int | None = None
    last_seen_at: datetime | None = None
    notes: str | None = None
    metadata_json: dict | None = None


class DeviceRead(Timestamped):
    organization_id: UUID
    branch_id: UUID
    hostname: str | None
    ip_address: str
    mac_address: str | None
    vendor: str | None
    operating_system: str | None
    device_type: DeviceType
    status: DeviceStatus
    latency_ms: int | None
    assigned_user: str | None
    department: str | None
    floor: str | None
    uptime_seconds: int | None
    last_seen_at: datetime | None
    notes: str | None
    metadata_json: dict


class ScanRequest(BaseModel):
    branch_id: UUID
    subnet_cidr: str | None = Field(default=None, examples=["192.168.1.0/24"])


class ScanSummary(BaseModel):
    branch_id: UUID
    scanned_hosts: int
    online_hosts: int
    message: str
    devices: list[DeviceRead]
