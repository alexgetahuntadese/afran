from fastapi import APIRouter

from app.api.routes import alerts, auth, dashboard, devices, printers, realtime, remote_support, scans, subscriptions

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(devices.router)
api_router.include_router(scans.router)
api_router.include_router(printers.router)
api_router.include_router(alerts.router)
api_router.include_router(subscriptions.router)
api_router.include_router(remote_support.router)
api_router.include_router(realtime.router)
