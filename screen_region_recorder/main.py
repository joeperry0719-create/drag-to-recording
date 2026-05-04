"""PySide6 application entry point."""

from __future__ import annotations

from pathlib import Path
import sys

from PySide6 import QtCore, QtGui, QtWidgets

from screen_region_recorder import icons
from screen_region_recorder.models import RecordingConfig, Region, ValidationError
from screen_region_recorder.preview_panel import REFERENCE_REGION, PreviewPanel
from screen_region_recorder.recorder import ScreenRecorder
from screen_region_recorder.selector import select_region
from screen_region_recorder.styles import app_stylesheet


APP_TITLE = "Drag to recording"


def format_elapsed(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def default_output_path() -> Path:
    videos = Path.home() / "Videos"
    parent = videos if videos.exists() else Path.cwd()
    return parent / "capture.mp4"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(icons.app_icon())
        self.resize(1200, 900)
        self.setMinimumSize(980, 740)

        self._selected_region: Region | None = None
        self._display_region = REFERENCE_REGION
        self._recorder = ScreenRecorder()
        self._recording_active = False
        self._stop_requested = False
        self._tray_icon: QtWidgets.QSystemTrayIcon | None = None

        self._progress_timer = QtCore.QTimer(self)
        self._progress_timer.setInterval(250)
        self._progress_timer.timeout.connect(self._refresh_recording_status)

        self._build_ui()
        self._set_ready_state()

    def _build_ui(self) -> None:
        root = QtWidgets.QWidget(self)
        root.setObjectName("Root")
        self.setCentralWidget(root)

        outer = QtWidgets.QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_title_area())

        content = QtWidgets.QWidget(root)
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(26, 24, 26, 26)
        content_layout.setSpacing(18)
        outer.addWidget(content, 1)

        helper = QtWidgets.QLabel("Select an area on screen and record it to MP4.", self)
        helper.setObjectName("HelperText")
        content_layout.addWidget(helper)

        main_row = QtWidgets.QHBoxLayout()
        main_row.setSpacing(24)
        main_row.addLayout(self._build_left_column(), 0)
        self.preview_panel = PreviewPanel(self)
        main_row.addWidget(self.preview_panel, 1)
        content_layout.addLayout(main_row, 1)

        content_layout.addWidget(self._build_action_card())
        content_layout.addLayout(self._build_options_row())
        content_layout.addWidget(self._build_status_card())

    def _build_title_area(self) -> QtWidgets.QWidget:
        title_area = QtWidgets.QWidget(self)
        title_area.setObjectName("TitleBar")
        title_area.setFixedHeight(66)
        layout = QtWidgets.QHBoxLayout(title_area)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(18)

        icon_label = QtWidgets.QLabel(title_area)
        icon_label.setPixmap(icons.app_icon(42).pixmap(42, 42))
        layout.addWidget(icon_label)

        title = QtWidgets.QLabel(APP_TITLE, title_area)
        title.setObjectName("AppTitle")
        layout.addWidget(title)
        layout.addStretch(1)
        return title_area

    def _build_left_column(self) -> QtWidgets.QVBoxLayout:
        column = QtWidgets.QVBoxLayout()
        column.setSpacing(16)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(self._build_output_card())
        column.addWidget(self._build_spin_card("FPS", "fps_spin", 1, 60, 15))
        column.addWidget(self._build_spin_card("Quality / CRF", "crf_spin", 0, 51, 23))
        column.addWidget(self._build_region_card())
        column.addStretch(1)
        return column

    def _build_card(self, title: str) -> tuple[QtWidgets.QWidget, QtWidgets.QVBoxLayout]:
        card = QtWidgets.QWidget(self)
        card.setObjectName("Card")
        card.setFixedWidth(470)
        card.setFixedHeight(116)
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(16)
        title_label = QtWidgets.QLabel(title, card)
        title_label.setObjectName("CardTitle")
        layout.addWidget(title_label)
        return card, layout

    def _build_output_card(self) -> QtWidgets.QWidget:
        card, layout = self._build_card("Output File")
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(18)
        self.output_edit = QtWidgets.QLineEdit(str(default_output_path()), card)
        self.output_edit.setMinimumWidth(300)
        self.browse_button = QtWidgets.QPushButton("Browse", card)
        self.browse_button.setFixedWidth(96)
        self.browse_button.clicked.connect(self._browse_output)
        row.addWidget(self.output_edit, 1)
        row.addWidget(self.browse_button)
        layout.addLayout(row)
        return card

    def _build_spin_card(
        self,
        label_text: str,
        attribute: str,
        minimum: int,
        maximum: int,
        value: int,
    ) -> QtWidgets.QWidget:
        card = QtWidgets.QWidget(self)
        card.setObjectName("Card")
        card.setFixedWidth(470)
        card.setFixedHeight(86)
        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(18)

        label = QtWidgets.QLabel(label_text, card)
        label.setObjectName("CardTitle")
        spinner = QtWidgets.QSpinBox(card)
        spinner.setRange(minimum, maximum)
        spinner.setValue(value)
        spinner.setFixedWidth(210)
        layout.addWidget(label, 1)
        layout.addWidget(spinner)
        setattr(self, attribute, spinner)
        return card

    def _build_region_card(self) -> QtWidgets.QWidget:
        card, layout = self._build_card("Selected Region")
        card.setFixedHeight(134)
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(10)
        self.region_value_labels: dict[str, QtWidgets.QLabel] = {}
        fields = [
            ("left", "Left:"),
            ("top", "Top:"),
            ("width", "Width:"),
            ("height", "Height:"),
        ]
        for column, (name, label_text) in enumerate(fields):
            label = QtWidgets.QLabel(label_text, card)
            label.setObjectName("FieldLabel")
            value = QtWidgets.QLabel(card)
            value.setObjectName("RegionValue")
            grid.addWidget(label, 0, column)
            grid.addWidget(value, 1, column)
            self.region_value_labels[name] = value
        layout.addLayout(grid)
        return card

    def _build_action_card(self) -> QtWidgets.QWidget:
        card = QtWidgets.QWidget(self)
        card.setObjectName("ActionCard")
        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(80, 18, 80, 18)
        layout.setSpacing(44)

        self.select_button = QtWidgets.QPushButton("Select Region", card)
        self.select_button.setIcon(icons.select_icon())
        self.select_button.setIconSize(QtCore.QSize(34, 34))
        self.select_button.setMinimumHeight(64)
        self.select_button.clicked.connect(self._select_region)

        self.start_button = QtWidgets.QPushButton("Start Recording", card)
        self.start_button.setObjectName("PrimaryButton")
        self.start_button.setIcon(icons.record_icon())
        self.start_button.setIconSize(QtCore.QSize(34, 34))
        self.start_button.setMinimumHeight(64)
        self.start_button.clicked.connect(self._start_recording_clicked)

        self.stop_button = QtWidgets.QPushButton("Stop Recording", card)
        self.stop_button.setIcon(icons.stop_icon())
        self.stop_button.setIconSize(QtCore.QSize(34, 34))
        self.stop_button.setMinimumHeight(64)
        self.stop_button.clicked.connect(self._stop_recording)

        layout.addWidget(self.select_button, 1)
        layout.addWidget(self.start_button, 1)
        layout.addWidget(self.stop_button, 1)
        return card

    def _build_options_row(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(8, 0, 0, 0)
        row.setSpacing(24)
        self.show_cursor_checkbox = QtWidgets.QCheckBox("Show cursor", self)
        self.show_cursor_checkbox.setChecked(False)
        self.show_cursor_checkbox.setEnabled(False)
        self.show_cursor_checkbox.setToolTip("Cursor capture is a future option.")
        row.addWidget(self.show_cursor_checkbox)

        divider = QtWidgets.QFrame(self)
        divider.setObjectName("VerticalDivider")
        divider.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        row.addWidget(divider)

        self.open_after_save_checkbox = QtWidgets.QCheckBox("Open file after saving", self)
        self.open_after_save_checkbox.setChecked(True)
        row.addWidget(self.open_after_save_checkbox)
        row.addStretch(1)
        return row

    def _build_status_card(self) -> QtWidgets.QWidget:
        card = QtWidgets.QWidget(self)
        card.setObjectName("StatusCard")
        card.setFixedHeight(84)
        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(26, 0, 26, 0)
        layout.setSpacing(20)
        self.status_icon_label = QtWidgets.QLabel(card)
        self.status_icon_label.setFixedSize(42, 42)
        self.status_text_label = QtWidgets.QLabel(card)
        self.status_text_label.setObjectName("StatusText")
        layout.addWidget(self.status_icon_label)
        layout.addWidget(self.status_text_label, 1)
        return card

    def _browse_output(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Choose MP4 output",
            self.output_edit.text().strip() or str(default_output_path()),
            "MP4 video (*.mp4)",
        )
        if path:
            if Path(path).suffix.lower() != ".mp4":
                path = f"{path}.mp4"
            self.output_edit.setText(path)

    def _select_region(self) -> None:
        previous_region = self._selected_region
        self._set_status("ready", "Select a screen region. Press Esc to cancel.")
        self.hide()
        QtWidgets.QApplication.processEvents()
        try:
            region = select_region(screen=QtWidgets.QApplication.primaryScreen())
        finally:
            self.show()
            self.raise_()
            self.activateWindow()

        if region is None:
            self._selected_region = previous_region
            self._set_status("ready", "Region selection canceled.")
            return
        self._selected_region = region
        self._display_region = region
        self._update_region_display(region)
        self.preview_panel.set_region(region)
        self._set_status("success", "Region selected.")

    def _start_recording_clicked(self) -> None:
        try:
            config = self._build_recording_config()
        except ValidationError as exc:
            self._show_error(str(exc))
            return

        self._set_status("recording", "Starting recording...")
        self.hide()
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(300, lambda: self._start_recording(config))

    def _build_recording_config(self) -> RecordingConfig:
        output_text = self.output_edit.text().strip()
        if not output_text:
            raise ValidationError("Choose an MP4 output path before recording.")
        if self._selected_region is None:
            raise ValidationError("Select a region before recording.")
        return RecordingConfig(
            region=self._selected_region,
            output_path=Path(output_text),
            fps=self.fps_spin.value(),
            crf=self.crf_spin.value(),
        )

    def _start_recording(self, config: RecordingConfig) -> None:
        try:
            self._recorder.start(config)
        except Exception as exc:
            self.show()
            self._set_ready_state()
            self._show_error(f"Could not start recording: {exc}")
            return

        self._recording_active = True
        self._stop_requested = False
        self._set_recording_state()
        self._show_tray_icon()
        self.showMinimized()
        self._progress_timer.start()

    def _stop_recording(self) -> None:
        if not self._recording_active or self._stop_requested:
            return
        self._stop_requested = True
        self._set_status("recording", "Stopping recording...")
        self._recorder.stop()

    def _refresh_recording_status(self) -> None:
        progress = self._recorder.progress
        prefix = "Stopping..." if self._stop_requested else "Recording..."
        self._set_status(
            "recording",
            f"{prefix} {format_elapsed(progress.elapsed_seconds)} · {progress.frame_count} frames",
        )

        if self._recording_active and not self._recorder.is_recording:
            self._finish_recording()

    def _finish_recording(self) -> None:
        self._progress_timer.stop()
        self._recorder.join(timeout=0.05)
        progress = self._recorder.progress
        self._recording_active = False
        self._stop_requested = False
        self._hide_tray_icon()
        self._set_ready_state()
        self.showNormal()
        self.raise_()
        self.activateWindow()

        if progress.last_error:
            self._show_error(progress.last_error)
            return

        self._set_status("success", "Recording stopped. File saved successfully.")
        if self.open_after_save_checkbox.isChecked() and progress.output_path is not None:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(progress.output_path)))

    def _show_tray_icon(self) -> None:
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            return
        if self._tray_icon is None:
            self._tray_icon = QtWidgets.QSystemTrayIcon(icons.app_icon(), self)
            menu = QtWidgets.QMenu(self)
            stop_action = menu.addAction(icons.stop_icon(), "Stop Recording")
            stop_action.triggered.connect(self._stop_recording)
            self._tray_icon.setContextMenu(menu)
            self._tray_icon.setToolTip(APP_TITLE)
        self._tray_icon.show()

    def _hide_tray_icon(self) -> None:
        if self._tray_icon is not None:
            self._tray_icon.hide()

    def _set_recording_state(self) -> None:
        self.select_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.browse_button.setEnabled(False)
        self.output_edit.setEnabled(False)
        self.fps_spin.setEnabled(False)
        self.crf_spin.setEnabled(False)

    def _set_ready_state(self) -> None:
        self.select_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.browse_button.setEnabled(True)
        self.output_edit.setEnabled(True)
        self.fps_spin.setEnabled(True)
        self.crf_spin.setEnabled(True)
        self._update_region_display(self._display_region)
        self.preview_panel.set_region(self._display_region)
        if not self.status_text_label.text():
            self._set_status("ready", "Ready to record.")

    def _update_region_display(self, region: Region) -> None:
        self.region_value_labels["left"].setText(str(region.left))
        self.region_value_labels["top"].setText(str(region.top))
        self.region_value_labels["width"].setText(str(region.width))
        self.region_value_labels["height"].setText(str(region.height))

    def _set_status(self, kind: str, text: str) -> None:
        self.status_icon_label.setPixmap(icons.status_icon(kind).pixmap(42, 42))
        self.status_text_label.setText(text)

    def _show_error(self, message: str) -> None:
        self._set_status("error", message)
        QtWidgets.QMessageBox.warning(self, APP_TITLE, message)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._recording_active:
            self._stop_recording()
            self.showNormal()
            event.ignore()
            return
        self._hide_tray_icon()
        super().closeEvent(event)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setWindowIcon(icons.app_icon())
    app.setStyleSheet(app_stylesheet())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
