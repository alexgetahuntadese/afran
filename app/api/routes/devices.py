from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import User
from app.repositories.devices import DeviceRepository
from app.schemas.devices import DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead])
async def list_devices(
    branch_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[DeviceRead]:
    repo = DeviceRepository(session)
    devices = await (repo.list_by_branch(branch_id) if branch_id else repo.list_by_org(user.organization_id))
    return devices


@router.patch("/{device_id}", response_model=DeviceRead)
async def update_device(
    device_id: UUID,
    data: DeviceUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> DeviceRead:
    try:
        device = await DeviceService(session).update(device_id, data)
        await session.commit()
        return device
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
