$ErrorActionPreference = "Stop"
$PyInstaller = Join-Path $PSScriptRoot "..\.venv\Scripts\pyinstaller.exe"

if (Test-Path $PyInstaller) {
    & $PyInstaller --noconfirm --windowed --name SmartITPlatform --add-data "app;app" app/ui/main.py
} else {
    pyinstaller --noconfirm --windowed --name SmartITPlatform --add-data "app;app" app/ui/main.py
}
