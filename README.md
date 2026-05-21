# Smart Hospital & Office IT Management Platform

Production-oriented Python desktop SaaS platform for LAN discovery, printer operations,
device inventory, realtime alerts, subscriptions, and LAN remote support.

## Run Backend

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[windows,network,dev]"
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

## Run Desktop

```powershell
python -m app.ui.main
```

## Services

- FastAPI REST and WebSocket backend
- SQLAlchemy async PostgreSQL persistence
- Redis-ready realtime event broadcasting
- Async LAN scanner with ping, hostname, MAC/vendor enrichment hooks
- Windows printer/spooler integration with pywin32 and PowerShell fallbacks
- Trial, Professional, and Enterprise feature gating
- PySide6 enterprise dashboard shell

## Database

```powershell
alembic upgrade head
```
