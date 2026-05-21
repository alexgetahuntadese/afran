# Windows Installer Notes

Use the PyInstaller output in `dist/SmartITPlatform` as the payload for an MSI or Inno Setup
installer. The installer should:

- install the desktop app under Program Files
- install backend service files under ProgramData
- register a Windows Service for `uvicorn app.main:app`
- register a Windows Service for `python -m app.workers.monitor`
- write `.env` with production secrets and database URLs
- configure auto-update checks against the organization license endpoint
