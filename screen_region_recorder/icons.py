"""Small generated icons used by the GUI."""

from __future__ import annotations

from PySide6 import QtCore, QtGui

from screen_region_recorder.styles import BLUE, GREEN, RED


def _pixmap(size: int = 32) -> tuple[QtGui.QPixmap, QtGui.QPainter]:
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    return pixmap, painter


def app_icon(size: int = 48) -> QtGui.QIcon:
    pixmap, painter = _pixmap(size)
    pen = QtGui.QPen(QtGui.QColor("#111111"), max(2, size // 18))
    painter.setPen(pen)
    margin = size * 0.18
    corner = size * 0.22

    lines = [
        (margin, margin, margin + corner, margin),
        (margin, margin, margin, margin + corner),
        (size - margin, margin, size - margin - corner, margin),
        (size - margin, margin, size - margin, margin + corner),
        (margin, size - margin, margin + corner, size - margin),
        (margin, size - margin, margin, size - margin - corner),
        (size - margin, size - margin, size - margin - corner, size - margin),
        (size - margin, size - margin, size - margin, size - margin - corner),
    ]
    for x1, y1, x2, y2 in lines:
        painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))

    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(QtGui.QColor(RED))
    dot = size * 0.22
    painter.drawEllipse(QtCore.QPointF(size / 2, size / 2), dot, dot)
    painter.end()
    return QtGui.QIcon(pixmap)


def select_icon(size: int = 32) -> QtGui.QIcon:
    pixmap, painter = _pixmap(size)
    pen = QtGui.QPen(QtGui.QColor("#111111"), max(2, size // 16))
    pen.setStyle(QtCore.Qt.PenStyle.DashLine)
    painter.setPen(pen)
    inset = size * 0.18
    painter.drawRect(QtCore.QRectF(inset, inset, size - 2 * inset, size - 2 * inset))
    painter.end()
    return QtGui.QIcon(pixmap)


def record_icon(size: int = 32) -> QtGui.QIcon:
    pixmap, painter = _pixmap(size)
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(QtGui.QColor("#ffffff"))
    painter.drawEllipse(QtCore.QPointF(size / 2, size / 2), size * 0.36, size * 0.36)
    painter.setBrush(QtGui.QColor(RED))
    painter.drawEllipse(QtCore.QPointF(size / 2, size / 2), size * 0.25, size * 0.25)
    painter.end()
    return QtGui.QIcon(pixmap)


def stop_icon(size: int = 32, color: str = "#8a8f96") -> QtGui.QIcon:
    pixmap, painter = _pixmap(size)
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(QtGui.QColor(color))
    side = size * 0.48
    painter.drawRect(QtCore.QRectF((size - side) / 2, (size - side) / 2, side, side))
    painter.end()
    return QtGui.QIcon(pixmap)


def status_icon(kind: str, size: int = 40) -> QtGui.QIcon:
    color = {
        "ready": GREEN,
        "success": GREEN,
        "recording": RED,
        "error": "#d92d20",
    }.get(kind, BLUE)
    pixmap, painter = _pixmap(size)
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(QtGui.QColor(color))
    painter.drawEllipse(QtCore.QPointF(size / 2, size / 2), size * 0.38, size * 0.38)

    pen = QtGui.QPen(QtGui.QColor("#ffffff"), max(2, size // 13))
    pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    if kind in {"ready", "success"}:
        painter.drawLine(
            QtCore.QPointF(size * 0.31, size * 0.51),
            QtCore.QPointF(size * 0.44, size * 0.64),
        )
        painter.drawLine(
            QtCore.QPointF(size * 0.44, size * 0.64),
            QtCore.QPointF(size * 0.70, size * 0.36),
        )
    elif kind == "error":
        painter.drawLine(
            QtCore.QPointF(size * 0.36, size * 0.36),
            QtCore.QPointF(size * 0.64, size * 0.64),
        )
        painter.drawLine(
            QtCore.QPointF(size * 0.64, size * 0.36),
            QtCore.QPointF(size * 0.36, size * 0.64),
        )
    else:
        painter.setBrush(QtGui.QColor("#ffffff"))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawEllipse(QtCore.QPointF(size / 2, size / 2), size * 0.14, size * 0.14)
    painter.end()
    return QtGui.QIcon(pixmap)
