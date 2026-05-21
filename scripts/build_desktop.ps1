$ErrorActionPreference = "Stop"
pyinstaller --noconfirm --windowed --name SmartITPlatform --add-data "app;app" app/ui/main.py
