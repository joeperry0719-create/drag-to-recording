"""Custom painted preview panel for the recording region."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from screen_region_recorder.models import Region
from screen_region_recorder.styles import BLUE, BORDER


REFERENCE_REGION = Region(320, 180, 1280, 720)
REFERENCE_SCREEN_WIDTH = 1920
REFERENCE_SCREEN_HEIGHT = 1080


def format_region_size(region: Region) -> str:
    return f"{region.width} × {region.height}"


def format_region_origin(region: Region) -> str:
    return f"{region.left}, {region.top}"


class PreviewPanel(QtWidgets.QWidget):
    """Illustrative monitor preview with a proportional selection rectangle."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._region = REFERENCE_REGION
        self.setMinimumSize(560, 420)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def set_region(self, region: Region | None) -> None:
        self._region = region or REFERENCE_REGION
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)

        panel = QtCore.QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setPen(QtGui.QPen(QtGui.QColor(BORDER), 1))
        painter.setBrush(QtGui.QColor("#ffffff"))
        painter.drawRoundedRect(panel, 8, 8)

        plot = panel.adjusted(52, 42, -32, -36)
        self._draw_grid(painter, plot)

        monitor_outer = self._monitor_rect(plot)
        monitor_screen = monitor_outer.adjusted(16, 16, -16, -16)
        self._draw_monitor(painter, monitor_outer, monitor_screen)
        selection = self._selection_rect(monitor_screen)
        self._draw_selection(painter, selection)

        painter.end()

    def _draw_grid(self, painter: QtGui.QPainter, plot: QtCore.QRectF) -> None:
        painter.save()
        grid_pen = QtGui.QPen(QtGui.QColor("#cfd3da"), 1)
        grid_pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        font = painter.font()
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("#111111"))

        x_values = [0, 640, 1280, 1920]
        y_values = [0, 360, 720, 1080]
        for value in x_values:
            x = plot.left() + plot.width() * (value / REFERENCE_SCREEN_WIDTH)
            painter.drawText(QtCore.QRectF(x - 35, plot.top() - 28, 70, 20), QtCore.Qt.AlignmentFlag.AlignCenter, str(value))
        for value in y_values:
            y = plot.top() + plot.height() * (value / REFERENCE_SCREEN_HEIGHT)
            painter.drawText(QtCore.QRectF(plot.left() - 48, y - 10, 38, 20), QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter, str(value))

        painter.setPen(grid_pen)
        for value in x_values:
            x = plot.left() + plot.width() * (value / REFERENCE_SCREEN_WIDTH)
            painter.drawLine(QtCore.QPointF(x, plot.top()), QtCore.QPointF(x, plot.bottom()))
        for value in y_values:
            y = plot.top() + plot.height() * (value / REFERENCE_SCREEN_HEIGHT)
            painter.drawLine(QtCore.QPointF(plot.left(), y), QtCore.QPointF(plot.right(), y))
        painter.restore()

    def _monitor_rect(self, plot: QtCore.QRectF) -> QtCore.QRectF:
        available_width = plot.width() * 0.84
        width = min(available_width, plot.height() * 1.55)
        height = width / 1.78
        x = plot.center().x() - width / 2
        y = plot.center().y() - height / 2 - 8
        return QtCore.QRectF(x, y, width, height)

    def _draw_monitor(
        self,
        painter: QtGui.QPainter,
        outer: QtCore.QRectF,
        screen: QtCore.QRectF,
    ) -> None:
        painter.save()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#24292c"))
        painter.drawRoundedRect(outer, 11, 11)

        gradient = QtGui.QLinearGradient(screen.topLeft(), screen.bottomRight())
        gradient.setColorAt(0.00, QtGui.QColor("#8cc2e9"))
        gradient.setColorAt(0.45, QtGui.QColor("#d9ecff"))
        gradient.setColorAt(1.00, QtGui.QColor("#397dbe"))
        painter.setBrush(gradient)
        painter.drawRect(screen)

        self._draw_wallpaper(painter, screen)

        stand_width = outer.width() * 0.23
        stand = QtCore.QRectF(
            outer.center().x() - stand_width / 2,
            outer.bottom(),
            stand_width,
            outer.height() * 0.20,
        )
        base = QtCore.QRectF(
            outer.center().x() - outer.width() * 0.17,
            stand.bottom() - 4,
            outer.width() * 0.34,
            outer.height() * 0.05,
        )
        stand_gradient = QtGui.QLinearGradient(stand.topLeft(), stand.bottomLeft())
        stand_gradient.setColorAt(0, QtGui.QColor("#373d40"))
        stand_gradient.setColorAt(1, QtGui.QColor("#252a2d"))
        painter.setBrush(stand_gradient)
        painter.drawRect(stand)
        painter.drawRoundedRect(base, 2, 2)
        painter.restore()

    def _draw_wallpaper(self, painter: QtGui.QPainter, screen: QtCore.QRectF) -> None:
        painter.save()
        painter.setClipRect(screen)
        center = QtCore.QPointF(screen.center().x() + screen.width() * 0.10, screen.center().y() + screen.height() * 0.06)
        for index in range(8):
            rect = QtCore.QRectF(
                center.x() - screen.width() * (0.32 - index * 0.018),
                center.y() - screen.height() * (0.24 - index * 0.012),
                screen.width() * (0.60 - index * 0.030),
                screen.height() * (0.44 - index * 0.020),
            )
            color = QtGui.QColor(190 - index * 9, 224 - index * 5, 255)
            color.setAlpha(155)
            pen = QtGui.QPen(color, 14 - index)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 20 * 16, 260 * 16)

        lower = QtGui.QLinearGradient(screen.bottomLeft(), screen.bottomRight())
        lower.setColorAt(0, QtGui.QColor(10, 92, 214, 165))
        lower.setColorAt(0.55, QtGui.QColor(0, 26, 94, 205))
        lower.setColorAt(1, QtGui.QColor(80, 160, 240, 140))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(lower)
        painter.drawPolygon(
            [
                QtCore.QPointF(screen.left(), screen.bottom() - screen.height() * 0.12),
                QtCore.QPointF(screen.left() + screen.width() * 0.52, screen.bottom() - screen.height() * 0.11),
                QtCore.QPointF(screen.left() + screen.width() * 0.72, screen.bottom()),
                QtCore.QPointF(screen.left(), screen.bottom()),
            ]
        )
        painter.restore()

    def _selection_rect(self, screen: QtCore.QRectF) -> QtCore.QRectF:
        region = self._region
        x = screen.left() + screen.width() * (region.left / REFERENCE_SCREEN_WIDTH)
        y = screen.top() + screen.height() * (region.top / REFERENCE_SCREEN_HEIGHT)
        width = screen.width() * (region.width / REFERENCE_SCREEN_WIDTH)
        height = screen.height() * (region.height / REFERENCE_SCREEN_HEIGHT)
        return QtCore.QRectF(x, y, width, height).intersected(screen)

    def _draw_selection(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.save()
        color = QtGui.QColor(BLUE)
        pen = QtGui.QPen(color, 2)
        pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

        painter.setPen(QtGui.QPen(color, 2))
        painter.setBrush(QtGui.QColor("#edf6ff"))
        handle = 11.0
        points = [
            rect.topLeft(),
            QtCore.QPointF(rect.center().x(), rect.top()),
            rect.topRight(),
            QtCore.QPointF(rect.left(), rect.center().y()),
            QtCore.QPointF(rect.right(), rect.center().y()),
            rect.bottomLeft(),
            QtCore.QPointF(rect.center().x(), rect.bottom()),
            rect.bottomRight(),
        ]
        for point in points:
            painter.drawRect(QtCore.QRectF(point.x() - handle / 2, point.y() - handle / 2, handle, handle))

        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(color)

        origin_text = format_region_origin(self._region)
        size_text = format_region_size(self._region)
        origin_rect = self._label_rect(painter, origin_text, rect.topLeft() + QtCore.QPointF(12, 12))
        size_rect = self._label_rect(
            painter,
            size_text,
            rect.bottomRight() - QtCore.QPointF(104, 34),
        )
        painter.drawRoundedRect(origin_rect, 4, 4)
        painter.drawRoundedRect(size_rect, 4, 4)
        painter.setPen(QtGui.QColor("#ffffff"))
        painter.drawText(origin_rect, QtCore.Qt.AlignmentFlag.AlignCenter, origin_text)
        painter.drawText(size_rect, QtCore.Qt.AlignmentFlag.AlignCenter, size_text)
        painter.restore()

    def _label_rect(
        self,
        painter: QtGui.QPainter,
        text: str,
        top_left: QtCore.QPointF,
    ) -> QtCore.QRectF:
        metrics = QtGui.QFontMetrics(painter.font())
        width = metrics.horizontalAdvance(text) + 16
        return QtCore.QRectF(top_left.x(), top_left.y(), width, 28)
