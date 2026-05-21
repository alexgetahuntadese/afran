from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.inventory.export_service import InventoryExportService
from app.models import User

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/export.csv")
async def export_csv(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    content = await InventoryExportService(session).csv_export(user.organization_id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="device-inventory.csv"'},
    )


@router.get("/export.pdf")
async def export_pdf(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    content = await InventoryExportService(session).pdf_export(user.organization_id)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="device-inventory.pdf"'},
    )
