import sys

from PySide6.QtWidgets import QApplication

from app.ui.backend_runner import ensure_local_backend
from app.ui.main_window import MainWindow
from app.ui.theme import DARK_STYLE


def main() -> int:
    ensure_local_backend()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
