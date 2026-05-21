from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import User
from app.remote_support.session_service import RemoteSupportService
from app.schemas.remote_support import RemoteSessionCreate, RemoteSessionRead

router = APIRouter(prefix="/remote-support", tags=["remote-support"])


@router.post("/sessions", response_model=RemoteSessionRead)
async def request_session(
    data: RemoteSessionCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> RemoteSessionRead:
    try:
        return await RemoteSupportService(session).request_session(user.organization_id, user.id, data)
    except PermissionError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/approve", response_model=RemoteSessionRead)
async def approve_session(
    session_id: UUID,
    approved_by_user: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> RemoteSessionRead:
    try:
        return await RemoteSupportService(session).approve(session_id, approved_by_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/end", response_model=RemoteSessionRead)
async def end_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> RemoteSessionRead:
    try:
        return await RemoteSupportService(session).end(session_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
