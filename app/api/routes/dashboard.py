from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.enums import AlertStatus, DeviceStatus
from app.models import Alert, Device, Printer, RemoteSession, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def summary(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    async def count(stmt) -> int:
        result = await session.execute(stmt)
        return int(result.scalar_one())

    return {
        "online_devices": await count(
            select(func.count(Device.id)).where(
                Device.organization_id == user.organization_id,
                Device.status == DeviceStatus.ONLINE,
            )
        ),
        "offline_devices": await count(
            select(func.count(Device.id)).where(
                Device.organization_id == user.organization_id,
                Device.status == DeviceStatus.OFFLINE,
            )
        ),
        "printer_issues": await count(
            select(func.count(Printer.id)).where(
                Printer.organization_id == user.organization_id,
                Printer.health_score < 80,
            )
        ),
        "active_alerts": await count(
            select(func.count(Alert.id)).where(
                Alert.organization_id == user.organization_id,
                Alert.status == AlertStatus.OPEN,
            )
        ),
        "remote_sessions": await count(
            select(func.count(RemoteSession.id)).where(
                RemoteSession.organization_id == user.organization_id,
            )
        ),
    }
