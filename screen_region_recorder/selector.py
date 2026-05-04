"""Screen region selection overlay."""

from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

from screen_region_recorder.models import MIN_REGION_SIZE, Region, ValidationError, normalize_region


class RegionSelector(QtWidgets.QWidget):
    """Full-screen overlay that returns a capture-space Region."""

    regionSelected = QtCore.Signal(object)
    selectionCanceled = QtCore.Signal()

    def __init__(
        self,
        screen: QtGui.QScreen | None = None,
        parent: QtWidgets.QWidget | None = None,
        *,
        min_size: int = MIN_REGION_SIZE,
    ) -> None:
        super().__init__(parent)
        self._screen = screen or QtWidgets.QApplication.primaryScreen()
        if self._screen is None:
            raise RuntimeError("No screen is available for region selection.")

        self._min_size = min_size
        self._origin: QtCore.QPoint | None = None
        self.selected_region: Region | None = None
        self.error_message: str | None = None
        self._rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Rectangle, self)

        self.setGeometry(self._screen.geometry())
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 80))
        super().paintEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.cancel()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        self.error_message = None
        self._origin = event.position().toPoint()
        self._rubber_band.setGeometry(QtCore.QRect(self._origin, QtCore.QSize()))
        self._rubber_band.show()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._origin is None:
            return
        current = event.position().toPoint()
        self._rubber_band.setGeometry(QtCore.QRect(self._origin, current).normalized())

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() != QtCore.Qt.MouseButton.LeftButton or self._origin is None:
            return

        current = event.position().toPoint()
        logical_rect = QtCore.QRect(self._origin, current).normalized()
        self._origin = None
        self._rubber_band.hide()

        try:
            self.selected_region = self._logical_rect_to_capture_region(logical_rect)
        except ValidationError as exc:
            self.error_message = str(exc)
            return

        self.hide()
        self.regionSelected.emit(self.selected_region)
        self.close()

    def cancel(self) -> None:
        self._rubber_band.hide()
        self.selected_region = None
        self.hide()
        self.selectionCanceled.emit()
        self.close()

    def _logical_rect_to_capture_region(self, rect: QtCore.QRect) -> Region:
        """Convert Qt logical screen coordinates to physical capture coordinates.

        Qt mouse events and QScreen.geometry() are reported in logical pixels.
        mss expects physical capture pixels. For the MVP we support the current
        primary screen first, so applying that screen's devicePixelRatio once at
        this boundary keeps the recorder and video writer independent of Qt.
        """

        screen_geometry = self._screen.geometry()
        dpr = self._screen.devicePixelRatio()
        global_left = screen_geometry.left() + rect.left()
        global_top = screen_geometry.top() + rect.top()
        global_right = screen_geometry.left() + rect.right() + 1
        global_bottom = screen_geometry.top() + rect.bottom() + 1

        start = (round(global_left * dpr), round(global_top * dpr))
        end = (round(global_right * dpr), round(global_bottom * dpr))
        return normalize_region(start, end, min_size=self._min_size).with_even_dimensions()


def select_region(
    screen: QtGui.QScreen | None = None,
    parent: QtWidgets.QWidget | None = None,
) -> Optional[Region]:
    """Open the selector and block only this local event loop until selection finishes."""

    selector = RegionSelector(screen=screen, parent=parent)
    loop = QtCore.QEventLoop()
    selector.regionSelected.connect(loop.quit)
    selector.selectionCanceled.connect(loop.quit)
    selector.destroyed.connect(loop.quit)
    selector.showFullScreen()
    selector.activateWindow()
    selector.raise_()
    loop.exec()
    return selector.selected_region
