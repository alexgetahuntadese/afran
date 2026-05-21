from fastapi import APIRouter

from app.api.routes import (
    alerts,
    auth,
    branches,
    dashboard,
    devices,
    inventory,
    payments,
    printers,
    realtime,
    remote_support,
    scans,
    subscriptions,
    topology,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(branches.router)
api_router.include_router(dashboard.router)
api_router.include_router(devices.router)
api_router.include_router(scans.router)
api_router.include_router(printers.router)
api_router.include_router(alerts.router)
api_router.include_router(subscriptions.router)
api_router.include_router(remote_support.router)
api_router.include_router(inventory.router)
api_router.include_router(payments.router)
api_router.include_router(topology.router)
api_router.include_router(realtime.router)
