import asyncio
import logging

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import Branch
from app.services.scanner_service import ScannerService

logger = logging.getLogger(__name__)


async def run_monitor_loop() -> None:
    settings = get_settings()
    while True:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Branch).where(Branch.subnet_cidr.is_not(None)))
                branches = list(result.scalars().all())
                for branch in branches:
                    await ScannerService(session).scan_branch(
                        branch.organization_id,
                        branch,
                        branch.subnet_cidr,
                    )
        except Exception:
            logger.exception("Background network scan failed")
        await asyncio.sleep(settings.scan_interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_monitor_loop())
