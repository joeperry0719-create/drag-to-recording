from pathlib import Path
import time

import numpy as np

from screen_region_recorder.models import RecordingConfig, Region
from screen_region_recorder.recorder import ScreenRecorder


class FakeWriter:
    def __init__(self) -> None:
        self.frames = []
        self.closed = False

    def write_frame(self, frame):
        self.frames.append(frame)

    def close(self):
        self.closed = True


class FailingCloseWriter(FakeWriter):
    def close(self):
        self.closed = True
        raise RuntimeError("writer close failed")


class FakeCapture:
    def __init__(self, frame: np.ndarray) -> None:
        self.frame = frame
        self.closed = False
        self.grab_count = 0

    def grab(self, monitor):
        self.grab_count += 1
        return self.frame

    def close(self):
        self.closed = True


class SlowCapture(FakeCapture):
    def __init__(self, frame: np.ndarray, delay_seconds: float) -> None:
        super().__init__(frame)
        self.delay_seconds = delay_seconds

    def grab(self, monitor):
        time.sleep(self.delay_seconds)
        return super().grab(monitor)


class FailingCapture(FakeCapture):
    def grab(self, monitor):
        self.grab_count += 1
        raise RuntimeError("capture failed")


def test_recorder_stops_worker_and_closes_resources():
    fake_writer = FakeWriter()
    fake_capture = FakeCapture(np.zeros((10, 10, 4), dtype=np.uint8))
    recorder = ScreenRecorder(
        writer_factory=lambda *args: fake_writer,
        capture_factory=lambda: fake_capture,
    )
    config = RecordingConfig(
        region=Region(0, 0, 10, 10),
        output_path=Path("capture.mp4"),
        fps=30,
        crf=23,
    )

    recorder.start(config)
    deadline = time.time() + 1.0
    while recorder.progress.frame_count == 0 and time.time() < deadline:
        time.sleep(0.01)
    recorder.stop()
    recorder.join(timeout=1.0)

    assert not recorder.is_recording
    assert fake_writer.closed
    assert fake_capture.closed
    assert recorder.progress.frame_count >= 1
    assert fake_writer.frames[-1].shape == (10, 10, 3)


def test_recorder_reports_capture_errors_and_closes_resources():
    fake_writer = FakeWriter()
    fake_capture = FailingCapture(np.zeros((10, 10, 4), dtype=np.uint8))
    recorder = ScreenRecorder(
        writer_factory=lambda *args: fake_writer,
        capture_factory=lambda: fake_capture,
    )
    config = RecordingConfig(
        region=Region(0, 0, 10, 10),
        output_path=Path("capture.mp4"),
        fps=30,
        crf=23,
    )

    recorder.start(config)
    recorder.join(timeout=1.0)

    assert not recorder.is_recording
    assert fake_writer.closed
    assert fake_capture.closed
    assert recorder.progress.last_error == "capture failed"


def test_recorder_closes_capture_even_if_writer_close_fails():
    fake_writer = FailingCloseWriter()
    fake_capture = FakeCapture(np.zeros((10, 10, 4), dtype=np.uint8))
    recorder = ScreenRecorder(
        writer_factory=lambda *args: fake_writer,
        capture_factory=lambda: fake_capture,
    )
    config = RecordingConfig(
        region=Region(0, 0, 10, 10),
        output_path=Path("capture.mp4"),
        fps=30,
        crf=23,
    )

    recorder.start(config)
    deadline = time.time() + 1.0
    while recorder.progress.frame_count == 0 and time.time() < deadline:
        time.sleep(0.01)
    recorder.stop()
    recorder.join(timeout=1.0)

    assert fake_writer.closed
    assert fake_capture.closed
    assert recorder.progress.last_error is not None
    assert "video writer close failed" in recorder.progress.last_error


def test_recorder_duplicates_frames_when_capture_falls_behind_target_fps():
    fake_writer = FakeWriter()
    fake_capture = SlowCapture(np.zeros((10, 10, 4), dtype=np.uint8), delay_seconds=0.08)
    fps = 30
    recorder = ScreenRecorder(
        writer_factory=lambda *args: fake_writer,
        capture_factory=lambda: fake_capture,
    )
    config = RecordingConfig(
        region=Region(0, 0, 10, 10),
        output_path=Path("capture.mp4"),
        fps=fps,
        crf=23,
    )

    recorder.start(config)
    time.sleep(0.30)
    recorder.stop()
    recorder.join(timeout=1.0)

    encoded_duration = recorder.progress.frame_count / fps
    assert not recorder.is_recording
    assert fake_capture.grab_count > 0
    assert recorder.progress.frame_count > fake_capture.grab_count
    assert encoded_duration >= recorder.progress.elapsed_seconds * 0.75
