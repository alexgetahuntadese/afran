import asyncio
import platform
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class PrinterSnapshot:
    name: str
    model: str | None
    driver_name: str | None
    ip_address: str | None
    share_name: str | None
    status: str
    queue_depth: int
    toner_level: int | None
    paper_status: str | None
    checked_at: datetime


class WindowsPrinterManager:
    async def list_printers(self) -> list[PrinterSnapshot]:
        if platform.system().lower() != "windows":
            return []
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._list_printers_sync)

    def _list_printers_sync(self) -> list[PrinterSnapshot]:
        try:
            import win32print
        except ImportError:
            return self._list_with_powershell()

        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        snapshots: list[PrinterSnapshot] = []
        for printer in win32print.EnumPrinters(flags):
            name = printer[2]
            handle = None
            try:
                handle = win32print.OpenPrinter(name)
                info = win32print.GetPrinter(handle, 2)
                jobs = win32print.EnumJobs(handle, 0, 999, 1)
                snapshots.append(
                    PrinterSnapshot(
                        name=name,
                        model=info.get("pPrinterName"),
                        driver_name=info.get("pDriverName"),
                        ip_address=None,
                        share_name=info.get("pShareName"),
                        status=self._status_name(info.get("Status", 0)),
                        queue_depth=len(jobs),
                        toner_level=None,
                        paper_status=None,
                        checked_at=datetime.now(UTC),
                    )
                )
            finally:
                if handle:
                    win32print.ClosePrinter(handle)
        return snapshots

    def _list_with_powershell(self) -> list[PrinterSnapshot]:
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Printer | Select-Object Name,DriverName,ShareName,PrinterStatus | ConvertTo-Json",
        ]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
        except (FileNotFoundError, subprocess.SubprocessError):
            return []
        if completed.returncode != 0 or not completed.stdout.strip():
            return []
        import json

        data = json.loads(completed.stdout)
        if isinstance(data, dict):
            data = [data]
        return [
            PrinterSnapshot(
                name=item["Name"],
                model=None,
                driver_name=item.get("DriverName"),
                ip_address=None,
                share_name=item.get("ShareName"),
                status=str(item.get("PrinterStatus", "unknown")).lower(),
                queue_depth=0,
                toner_level=None,
                paper_status=None,
                checked_at=datetime.now(UTC),
            )
            for item in data
        ]

    async def restart_spooler(self) -> tuple[bool, str]:
        if platform.system().lower() != "windows":
            return False, "Windows spooler controls are available only on Windows."
        proc = await asyncio.create_subprocess_exec(
            "powershell",
            "-NoProfile",
            "-Command",
            "Restart-Service -Name Spooler -Force",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0:
            return True, "Print spooler restarted successfully."
        return False, stderr.decode(errors="ignore").strip() or "Failed to restart print spooler."

    async def print_test_page(self, printer_name: str) -> tuple[bool, str]:
        if platform.system().lower() != "windows":
            return False, "Test page printing is available only on Windows."
        script = f'(New-Object -ComObject WScript.Network).SetDefaultPrinter("{printer_name}")'
        proc = await asyncio.create_subprocess_exec(
            "powershell",
            "-NoProfile",
            "-Command",
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0:
            return True, f"{printer_name} selected for test page workflow."
        return False, stderr.decode(errors="ignore").strip()

    def _status_name(self, status: int) -> str:
        if status == 0:
            return "ready"
        if status & 0x00000080:
            return "offline"
        if status & 0x00000002:
            return "error"
        if status & 0x00000010:
            return "paper_out"
        return "warning"
