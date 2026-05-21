from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from app.ui.api_client import ApiClient, ApiSession
from app.ui.components.metric_card import MetricCard


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Hospital & Office IT Management Platform")
        self.resize(1280, 780)
        self.api = ApiClient(ApiSession())
        self.metrics: dict[str, MetricCard] = {}
        self.stack = QStackedWidget()
        self._build()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)

    def _build(self) -> None:
        root = QWidget()
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(self._sidebar())
        shell.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.stack.addWidget(self._login_view())
        self.stack.addWidget(self._dashboard_view())

    def _sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(236)
        layout = QVBoxLayout(sidebar)
        title = QLabel("Smart IT")
        title.setStyleSheet("font-size: 22px; font-weight: 700; padding: 14px 8px;")
        layout.addWidget(title)
        for label in ("Dashboard", "Devices", "Printers", "Alerts", "Remote Support", "Inventory"):
            button = QPushButton(label)
            button.clicked.connect(lambda _, index=1: self.stack.setCurrentIndex(index))
            layout.addWidget(button)
        layout.addStretch()
        return sidebar

    def _login_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(320, 120, 320, 120)
        title = QLabel("Operator Sign In")
        title.setStyleSheet("font-size: 30px; font-weight: 700;")
        self.organization = QLineEdit()
        self.organization.setPlaceholderText("Organization for first launch")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Full name")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.subnet = QLineEdit()
        self.subnet.setPlaceholderText("LAN subnet, for example 192.168.1.0/24")
        login = QPushButton("Sign in")
        login.setObjectName("PrimaryButton")
        login.clicked.connect(self.login)
        bootstrap = QPushButton("Create workspace")
        bootstrap.clicked.connect(self.bootstrap)
        layout.addWidget(title)
        layout.addSpacing(16)
        for widget in (self.organization, self.name, self.email, self.password, self.subnet, login, bootstrap):
            layout.addWidget(widget)
        layout.addStretch()
        return view

    def _dashboard_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(24, 24, 24, 24)
        header = QLabel("Operations Dashboard")
        header.setStyleSheet("font-size: 26px; font-weight: 700;")
        layout.addWidget(header)

        grid = QGridLayout()
        for index, (key, title) in enumerate(
            {
                "online_devices": "Online devices",
                "offline_devices": "Offline devices",
                "printer_issues": "Printer issues",
                "active_alerts": "Active alerts",
                "remote_sessions": "Remote sessions",
                "recent_scans": "Recent scans",
            }.items()
        ):
            card = MetricCard(title)
            self.metrics[key] = card
            grid.addWidget(card, index // 3, index % 3)
        layout.addLayout(grid)

        self.device_table = QTableWidget(0, 6)
        self.device_table.setHorizontalHeaderLabels(["Hostname", "IP", "MAC", "Vendor", "Type", "Status"])
        layout.addWidget(QLabel("Discovered Devices"))
        layout.addWidget(self.device_table, 1)

        self.alert_table = QTableWidget(0, 4)
        self.alert_table.setHorizontalHeaderLabels(["Severity", "Title", "Message", "Status"])
        layout.addWidget(QLabel("Alert Center"))
        layout.addWidget(self.alert_table, 1)
        return view

    def login(self) -> None:
        try:
            self.api.login(self.email.text(), self.password.text())
            self._enter_app()
        except Exception as exc:
            QMessageBox.warning(self, "Sign in failed", str(exc))

    def bootstrap(self) -> None:
        try:
            self.api.bootstrap(
                self.organization.text(),
                self.name.text(),
                self.email.text(),
                self.password.text(),
            )
            self._enter_app()
            self.auto_scan()
        except Exception as exc:
            QMessageBox.warning(self, "Workspace setup failed", str(exc))

    def _enter_app(self) -> None:
        self.stack.setCurrentIndex(1)
        self.refresh_timer.start(30_000)
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            summary = self.api.dashboard()
            devices = self.api.devices()
            alerts = self.api.alerts()
        except Exception as exc:
            QMessageBox.warning(self, "Backend unavailable", str(exc))
            return
        for key, value in summary.items():
            if key in self.metrics:
                self.metrics[key].set_value(value)
        self.metrics["recent_scans"].set_value("Live")
        self._fill_table(
            self.device_table,
            devices,
            ["hostname", "ip_address", "mac_address", "vendor", "device_type", "status"],
        )
        self._fill_table(self.alert_table, alerts, ["severity", "title", "message", "status"])

    def auto_scan(self) -> None:
        try:
            branches = self.api.branches()
            if not branches:
                return
            summary = self.api.run_scan(branches[0]["id"], self.subnet.text() or None)
            QMessageBox.information(self, "LAN scan complete", summary["message"])
            self.refresh_data()
        except Exception as exc:
            QMessageBox.warning(self, "LAN scan failed", str(exc))

    def _fill_table(self, table: QTableWidget, rows: list[dict], keys: list[str]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, key in enumerate(keys):
                value = row.get(key)
                table.setItem(row_index, column_index, QTableWidgetItem("" if value is None else str(value)))
        table.resizeColumnsToContents()
