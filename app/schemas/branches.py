from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import Timestamped


class BranchRead(Timestamped):
    organization_id: UUID
    name: str
    location: str | None
    subnet_cidr: str | None


class BranchUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    subnet_cidr: str | None = None
