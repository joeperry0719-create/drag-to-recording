"""Application theme for the PySide6 GUI."""

from __future__ import annotations


BLUE = "#1f7ae8"
BLUE_DARK = "#0967d8"
RED = "#ed2b3a"
GREEN = "#4ca83d"
TEXT = "#111827"
MUTED = "#6b7280"
BORDER = "#d6d9df"
PANEL = "#ffffff"
BACKGROUND = "#f7f8fa"


def app_stylesheet() -> str:
    return f"""
    QMainWindow {{
        background: {BACKGROUND};
    }}

    QWidget#Root {{
        background: {BACKGROUND};
        color: {TEXT};
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 16px;
    }}

    QWidget#TitleBar {{
        background: {PANEL};
        border-bottom: 1px solid {BORDER};
    }}

    QLabel#AppTitle {{
        color: #111111;
        font-size: 21px;
        font-weight: 600;
    }}

    QLabel#HelperText {{
        color: #111111;
        font-size: 17px;
    }}

    QWidget#Card, QWidget#ActionCard, QWidget#StatusCard {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}

    QLabel#CardTitle {{
        color: #111111;
        font-size: 18px;
        font-weight: 700;
    }}

    QLabel#FieldLabel {{
        color: #111111;
        font-size: 17px;
    }}

    QLabel#RegionValue {{
        color: #111111;
        font-size: 20px;
        font-weight: 600;
    }}

    QLineEdit, QSpinBox {{
        background: #ffffff;
        color: #111111;
        border: 1px solid #b8bcc4;
        border-radius: 4px;
        padding: 8px 12px;
        min-height: 36px;
        selection-background-color: {BLUE};
    }}

    QLineEdit:focus, QSpinBox:focus {{
        border: 1px solid {BLUE};
    }}

    QPushButton {{
        background: #ffffff;
        color: #111111;
        border: 1px solid #b8bcc4;
        border-radius: 6px;
        padding: 10px 18px;
        font-size: 17px;
        font-weight: 500;
        min-height: 42px;
    }}

    QPushButton:hover {{
        background: #f7f9fc;
        border-color: #9da3af;
    }}

    QPushButton:pressed {{
        background: #edf2f8;
    }}

    QPushButton:disabled {{
        color: #7d828a;
        background: #f9fafb;
        border-color: #cfd3da;
    }}

    QPushButton#PrimaryButton {{
        background: {BLUE};
        color: #ffffff;
        border: 1px solid {BLUE_DARK};
        font-size: 18px;
        font-weight: 600;
    }}

    QPushButton#PrimaryButton:hover {{
        background: #166fe0;
    }}

    QPushButton#PrimaryButton:pressed {{
        background: {BLUE_DARK};
    }}

    QPushButton#PrimaryButton:disabled {{
        background: #9fc5f8;
        color: #eef6ff;
        border-color: #9fc5f8;
    }}

    QCheckBox {{
        color: #111111;
        font-size: 17px;
        spacing: 12px;
    }}

    QCheckBox:disabled {{
        color: #7d828a;
    }}

    QFrame#VerticalDivider {{
        color: #bec3cb;
        background: #bec3cb;
        max-width: 1px;
    }}

    QLabel#StatusText {{
        color: #111111;
        font-size: 19px;
    }}
    """
