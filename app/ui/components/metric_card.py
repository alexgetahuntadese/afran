from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "0") -> None:
        super().__init__()
        self.setMinimumHeight(96)
        self.setStyleSheet("QFrame { border: 1px solid #2e3a46; border-radius: 8px; padding: 10px; }")
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setObjectName("Muted")
        self.value = QLabel(value)
        self.value.setObjectName("Metric")
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addStretch()

    def set_value(self, value: str | int) -> None:
        self.value.setText(str(value))
