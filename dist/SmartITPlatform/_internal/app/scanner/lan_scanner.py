import asyncio
import ipaddress
import platform
import socket
import subprocess
import time
from dataclasses import dataclass

from app.core.enums import DeviceStatus, DeviceType
from app.scanner.vendor_lookup import lookup_vendor


@dataclass(frozen=True)
class DiscoveredHost:
    ip_address: str
    hostname: str | None
    mac_address: str | None
    vendor: str | None
    operating_system: str | None
    device_type: DeviceType
    status: DeviceStatus
    latency_ms: int | None


class LANScanner:
    def __init__(self, concurrency: int = 128, timeout_seconds: float = 1.0) -> None:
        self.concurrency = concurrency
        self.timeout_seconds = timeout_seconds

    async def scan(self, subnet_cidr: str) -> list[DiscoveredHost]:
        network = ipaddress.ip_network(subnet_cidr, strict=False)
        semaphore = asyncio.Semaphore(self.concurrency)
        tasks = [self._scan_host(str(ip), semaphore) for ip in network.hosts()]
        return [host for host in await asyncio.gather(*tasks) if host is not None]

    async def _scan_host(
        self, ip_address: str, semaphore: asyncio.Semaphore
    ) -> DiscoveredHost | None:
        async with semaphore:
            started = time.perf_counter()
            online = await self._ping(ip_address)
            latency = int((time.perf_counter() - started) * 1000) if online else None
            hostname = await self._hostname(ip_address) if online else None
            mac = await self._arp_mac(ip_address) if online else None
            vendor = lookup_vendor(mac)
            return DiscoveredHost(
                ip_address=ip_address,
                hostname=hostname,
                mac_address=mac,
                vendor=vendor,
                operating_system=self._infer_os(hostname, vendor),
                device_type=self._infer_type(hostname, vendor),
                status=DeviceStatus.ONLINE if online else DeviceStatus.OFFLINE,
                latency_ms=latency,
            )

    async def _ping(self, ip_address: str) -> bool:
        system = platform.system().lower()
        args = ["ping", "-n", "1", "-w", str(int(self.timeout_seconds * 1000)), ip_address]
        if system != "windows":
            args = ["ping", "-c", "1", "-W", str(int(self.timeout_seconds)), ip_address]
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return await proc.wait() == 0
        except (FileNotFoundError, PermissionError):
            return await self._tcp_probe(ip_address)

    async def _tcp_probe(self, ip_address: str) -> bool:
        for port in (80, 443, 445, 9100, 631):
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip_address, port), timeout=self.timeout_seconds
                )
                writer.close()
                await writer.wait_closed()
                return True
            except OSError:
                continue
        return False

    async def _hostname(self, ip_address: str) -> str | None:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, lambda: socket.gethostbyaddr(ip_address)[0])
        except (socket.herror, socket.gaierror, TimeoutError):
            return None

    async def _arp_mac(self, ip_address: str) -> str | None:
        def read_arp() -> str | None:
            try:
                output = subprocess.check_output(["arp", "-a", ip_address], text=True, timeout=2)
            except (subprocess.SubprocessError, FileNotFoundError):
                return None
            for line in output.splitlines():
                if ip_address in line:
                    parts = line.split()
                    for part in parts:
                        if "-" in part and len(part) >= 17:
                            return part.replace("-", ":").upper()
                        if ":" in part and len(part) >= 17:
                            return part.upper()
            return None

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, read_arp)

    def _infer_type(self, hostname: str | None, vendor: str | None) -> DeviceType:
        text = f"{hostname or ''} {vendor or ''}".lower()
        if "zebra" in text:
            return DeviceType.ZEBRA_PRINTER
        if "epson" in text or "thermal" in text:
            return DeviceType.THERMAL_PRINTER
        if "hp" in text or "hewlett" in text or "printer" in text:
            return DeviceType.PRINTER
        if "server" in text:
            return DeviceType.SERVER
        if "cisco" in text or "router" in text or "gateway" in text:
            return DeviceType.ROUTER
        if "switch" in text or "ubiquiti" in text:
            return DeviceType.SWITCH
        return DeviceType.UNKNOWN

    def _infer_os(self, hostname: str | None, vendor: str | None) -> str | None:
        text = f"{hostname or ''} {vendor or ''}".lower()
        if "windows" in text or "desktop" in text or "pc" in text:
            return "Windows"
        if "zebra" in text:
            return "Zebra Link-OS"
        return None
