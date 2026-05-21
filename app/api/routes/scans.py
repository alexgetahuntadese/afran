from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Branch, User
from app.schemas.devices import ScanRequest, ScanSummary
from app.services.scanner_service import ScannerService

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/run", response_model=ScanSummary)
async def run_scan(
    data: ScanRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ScanSummary:
    branch = await session.get(Branch, data.branch_id)
    if branch is None or branch.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Branch not found")
    try:
        return await ScannerService(session).scan_branch(user.organization_id, branch, data.subnet_cidr)
    except PermissionError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc
