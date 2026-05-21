from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class RemoteMessageType(StrEnum):
    HELLO = "hello"
    PERMISSION_REQUEST = "permission_request"
    PERMISSION_DECISION = "permission_decision"
    SCREEN_FRAME = "screen_frame"
    POINTER_EVENT = "pointer_event"
    KEYBOARD_EVENT = "keyboard_event"
    CHAT = "chat"
    HEARTBEAT = "heartbeat"
    END = "end"


class RemoteSupportMessage(BaseModel):
    type: RemoteMessageType
    session_id: UUID
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict


class PermissionPayload(BaseModel):
    technician_name: str
    device_name: str
    requested_control: bool = True
    recording_enabled: bool = True


class ScreenFramePayload(BaseModel):
    width: int
    height: int
    encoding: str = "jpeg"
    sequence: int
    data_base64: str


class PointerEventPayload(BaseModel):
    x: int
    y: int
    button: str | None = None
    pressed: bool | None = None


class KeyboardEventPayload(BaseModel):
    key: str
    pressed: bool
    modifiers: list[str] = []
