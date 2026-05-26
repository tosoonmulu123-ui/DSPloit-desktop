"""
DSPloit PC Theme — dark theme matching iOS app aesthetic.
"""

DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: "Segoe UI", "SF Pro", sans-serif;
    font-size: 13px;
}
QPushButton {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0f3460;
    border-color: #533483;
}
QPushButton:pressed {
    background-color: #533483;
}
QPushButton:disabled {
    background-color: #0d1b2a;
    color: #555;
}
QPushButton#jailbreakBtn {
    background-color: #e94560;
    color: white;
    font-size: 16px;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
}
QPushButton#jailbreakBtn:hover {
    background-color: #ff6b6b;
}
QLabel {
    color: #e0e0e0;
}
QLabel#title {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#subtitle {
    font-size: 12px;
    color: #888;
}
QLabel#status_ok {
    color: #4ecdc4;
}
QLabel#status_error {
    color: #e94560;
}
QTextEdit, QPlainTextEdit {
    background-color: #0d1b2a;
    color: #4ecdc4;
    border: 1px solid #16213e;
    border-radius: 4px;
    font-family: "Cascadia Code", "Fira Code", monospace;
    font-size: 12px;
    padding: 8px;
}
QListWidget {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 4px;
}
QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #0d1b2a;
}
QListWidget::item:selected {
    background-color: #533483;
}
QTabWidget::pane {
    border: 1px solid #0f3460;
    background-color: #1a1a2e;
}
QTabBar::tab {
    background-color: #16213e;
    color: #888;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #0f3460;
    color: #ffffff;
}
QProgressBar {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 4px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background-color: #4ecdc4;
    border-radius: 3px;
}
QGroupBox {
    border: 1px solid #0f3460;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
}
QGroupBox::title {
    color: #4ecdc4;
    subcontrol-origin: margin;
    left: 12px;
}
QScrollBar:vertical {
    background-color: #0d1b2a;
    width: 8px;
}
QScrollBar::handle:vertical {
    background-color: #533483;
    border-radius: 4px;
    min-height: 20px;
}
"""
