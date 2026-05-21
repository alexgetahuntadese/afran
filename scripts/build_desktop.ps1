$ErrorActionPreference = "Stop"
$PyInstaller = Join-Path $PSScriptRoot "..\.venv\Scripts\pyinstaller.exe"

if (Test-Path $PyInstaller) {
    & $PyInstaller --noconfirm --windowed --name SmartITPlatform --add-data "app;app" --hidden-import aiosqlite --hidden-import sqlalchemy.dialects.sqlite.aiosqlite --hidden-import passlib.handlers.bcrypt app/ui/main.py
} else {
    pyinstaller --noconfirm --windowed --name SmartITPlatform --add-data "app;app" --hidden-import aiosqlite --hidden-import sqlalchemy.dialects.sqlite.aiosqlite --hidden-import passlib.handlers.bcrypt app/ui/main.py
}
