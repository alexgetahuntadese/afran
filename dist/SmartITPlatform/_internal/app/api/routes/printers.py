from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Printer, User
from app.printers.printer_service import PrinterService
from app.schemas.printers import PrinterActionResponse, PrinterRead

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("", response_model=list[PrinterRead])
async def list_printers(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[PrinterRead]:
    result = await session.execute(select(Printer).where(Printer.organization_id == user.organization_id))
    return list(result.scalars().all())


@router.post("/sync/{branch_id}", response_model=list[PrinterRead])
async def sync_printers(
    branch_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[PrinterRead]:
    printers = await PrinterService(session).sync_local_printers(user.organization_id, branch_id)
    await session.commit()
    return printers


@router.post("/spooler/restart", response_model=PrinterActionResponse)
async def restart_spooler(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> PrinterActionResponse:
    return await PrinterService(session).restart_spooler()


@router.post("/{printer_name}/test-page", response_model=PrinterActionResponse)
async def test_page(
    printer_name: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> PrinterActionResponse:
    try:
        return await PrinterService(session).print_test_page(printer_name)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
