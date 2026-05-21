from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Printer
from app.printers.windows_printer import WindowsPrinterManager
from app.schemas.printers import PrinterActionResponse


class PrinterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.windows = WindowsPrinterManager()

    async def sync_local_printers(self, organization_id: UUID, branch_id: UUID) -> list[Printer]:
        snapshots = await self.windows.list_printers()
        printers: list[Printer] = []
        for snapshot in snapshots:
            result = await self.session.execute(
                select(Printer).where(Printer.branch_id == branch_id, Printer.name == snapshot.name)
            )
            printer = result.scalar_one_or_none()
            if printer is None:
                printer = Printer(organization_id=organization_id, branch_id=branch_id, name=snapshot.name)
                self.session.add(printer)
            printer.model = snapshot.model
            printer.driver_name = snapshot.driver_name
            printer.ip_address = snapshot.ip_address
            printer.share_name = snapshot.share_name
            printer.status = snapshot.status
            printer.queue_depth = snapshot.queue_depth
            printer.toner_level = snapshot.toner_level
            printer.paper_status = snapshot.paper_status
            printer.last_checked_at = snapshot.checked_at
            printer.health_score = self._health_score(printer)
            printers.append(printer)
        await self.session.flush()
        return printers

    async def restart_spooler(self) -> PrinterActionResponse:
        ok, message = await self.windows.restart_spooler()
        return PrinterActionResponse(action="restart_spooler", ok=ok, message=message)

    async def print_test_page(self, printer_name: str) -> PrinterActionResponse:
        ok, message = await self.windows.print_test_page(printer_name)
        return PrinterActionResponse(action="print_test_page", ok=ok, message=message)

    def _health_score(self, printer: Printer) -> int:
        score = 100
        if printer.status.lower() != "ready":
            score -= 45
        if printer.queue_depth > 10:
            score -= 20
        if printer.toner_level is not None and printer.toner_level < 15:
            score -= 20
        if printer.paper_status and printer.paper_status.lower() != "ok":
            score -= 15
        return max(score, 0)
