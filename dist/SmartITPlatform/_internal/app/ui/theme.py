DARK_STYLE = """
QWidget {
    background: #101418;
    color: #e7edf3;
    font-family: "Segoe UI";
    font-size: 13px;
}
QFrame#Sidebar {
    background: #151b21;
    border-right: 1px solid #26313a;
}
QPushButton {
    background: #1d2630;
    border: 1px solid #2e3a46;
    border-radius: 6px;
    padding: 8px 10px;
    text-align: left;
}
QPushButton:hover {
    background: #26313c;
}
QPushButton#NavButton {
    text-align: left;
    border: 0;
}
QPushButton#NavButton:checked {
    background: #2f7df6;
    color: white;
}
QPushButton#PrimaryButton {
    background: #2f7df6;
    color: white;
    border: 1px solid #2f7df6;
    text-align: center;
}
QLineEdit {
    background: #151b21;
    border: 1px solid #2e3a46;
    border-radius: 6px;
    padding: 8px;
}
QTableWidget {
    background: #101418;
    alternate-background-color: #131a20;
    gridline-color: #26313a;
    border: 1px solid #26313a;
    border-radius: 6px;
}
QHeaderView::section {
    background: #151b21;
    color: #aeb9c5;
    border: 0;
    padding: 8px;
}
QLabel#Metric {
    font-size: 28px;
    font-weight: 700;
}
QLabel#Muted {
    color: #8c9aa8;
}
"""

LIGHT_STYLE = """
QWidget {
    background: #f6f8fb;
    color: #17202a;
    font-family: "Segoe UI";
    font-size: 13px;
}
QFrame#Sidebar {
    background: #ffffff;
    border-right: 1px solid #dde4ec;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #d7e0ea;
    border-radius: 6px;
    padding: 8px 10px;
    text-align: left;
}
QPushButton:hover {
    background: #edf3fa;
}
QPushButton#NavButton {
    text-align: left;
    border: 0;
}
QPushButton#NavButton:checked {
    background: #2563eb;
    color: white;
}
QPushButton#PrimaryButton {
    background: #2563eb;
    color: white;
    border: 1px solid #2563eb;
    text-align: center;
}
QLineEdit {
    background: #ffffff;
    border: 1px solid #d7e0ea;
    border-radius: 6px;
    padding: 8px;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fbfe;
    gridline-color: #dde4ec;
    border: 1px solid #dde4ec;
    border-radius: 6px;
}
QHeaderView::section {
    background: #eef3f8;
    color: #52616f;
    border: 0;
    padding: 8px;
}
QLabel#Metric {
    font-size: 28px;
    font-weight: 700;
}
QLabel#Muted {
    color: #697887;
}
"""
