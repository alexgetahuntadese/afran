from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.alert_service import AlertService
from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import User
from app.repositories.alerts import AlertRepository
from app.schemas.alerts import AlertRead

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
async def list_open_alerts(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[AlertRead]:
    return await AlertRepository(session).open_for_org(user.organization_id)


@router.post("/{alert_id}/acknowledge", response_model=AlertRead)
async def acknowledge_alert(
    alert_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> AlertRead:
    try:
        alert = await AlertService(session).acknowledge(alert_id, user.id)
        await session.commit()
        return alert
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
