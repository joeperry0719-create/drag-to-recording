"""Screen recording engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
import time
from typing import Any, Callable, Protocol

import mss
import numpy as np

from screen_region_recorder.models import RecordingConfig
from screen_region_recorder.video_writer import VideoWriter


class CaptureBackend(Protocol):
    def grab(self, monitor: dict[str, int]) -> Any:
        ...

    def close(self) -> None:
        ...


class FrameWriter(Protocol):
    def write_frame(self, frame: np.ndarray) -> None:
        ...

    def close(self) -> None:
        ...


@dataclass(frozen=True)
class RecordingProgress:
    elapsed_seconds: float = 0.0
    frame_count: int = 0
    last_error: str | None = None
    output_path: Path | None = None


WriterFactory = Callable[[Path, int, int, int, int], FrameWriter]
CaptureFactory = Callable[[], CaptureBackend]


class ScreenRecorder:
    """Capture a validated screen region to MP4 on a worker thread."""

    def __init__(
        self,
        *,
        writer_factory: WriterFactory | None = None,
        capture_factory: CaptureFactory | None = None,
    ) -> None:
        self._writer_factory = writer_factory or VideoWriter
        self._capture_factory = capture_factory or mss.MSS
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._progress = RecordingProgress()
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        thread = self._thread
        return thread is not None and thread.is_alive()

    @property
    def progress(self) -> RecordingProgress:
        with self._lock:
            return self._progress

    def start(self, config: RecordingConfig) -> None:
        if self.is_recording:
            raise RuntimeError("Recording is already in progress.")
        self._stop_event = threading.Event()
        self._set_progress(RecordingProgress(output_path=config.output_path))
        self._thread = threading.Thread(
            target=self._run,
            args=(config,),
            name="ScreenRegionRecorder",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def join(self, timeout: float | None = None) -> None:
        thread = self._thread
        if thread is not None:
            thread.join(timeout)

    def _run(self, config: RecordingConfig) -> None:
        region = config.encoder_region
        monitor = region.as_mss_monitor()
        writer: FrameWriter | None = None
        capture: CaptureBackend | None = None
        frame_count = 0
        start_time = time.perf_counter()
        frame_interval = 1.0 / config.fps
        last_error: str | None = None

        try:
            writer = self._writer_factory(
                config.output_path,
                region.width,
                region.height,
                config.fps,
                config.crf,
            )
            capture = self._capture_factory()

            while not self._stop_event.is_set():
                now = time.perf_counter()
                next_frame_at = start_time + (frame_count * frame_interval)
                delay = next_frame_at - now
                if delay > 0 and self._stop_event.wait(delay):
                    break

                screenshot = capture.grab(monitor)
                frame = self._bgra_to_rgb(screenshot)

                elapsed = time.perf_counter() - start_time
                target_frame_count = max(frame_count + 1, int(elapsed * config.fps) + 1)
                while frame_count < target_frame_count:
                    writer.write_frame(frame)
                    frame_count += 1

                self._set_progress(
                    RecordingProgress(
                        elapsed_seconds=elapsed,
                        frame_count=frame_count,
                        output_path=config.output_path,
                    )
                )
        except Exception as exc:
            last_error = str(exc)
        finally:
            elapsed = time.perf_counter() - start_time
            close_errors = []
            if writer is not None:
                try:
                    writer.close()
                except Exception as exc:
                    close_errors.append(f"video writer close failed: {exc}")
            if capture is not None:
                try:
                    capture.close()
                except Exception as exc:
                    close_errors.append(f"capture backend close failed: {exc}")
            if close_errors and last_error is None:
                last_error = "; ".join(close_errors)
            self._set_progress(
                RecordingProgress(
                    elapsed_seconds=elapsed,
                    frame_count=frame_count,
                    last_error=last_error,
                    output_path=config.output_path,
                )
            )

    def _set_progress(self, progress: RecordingProgress) -> None:
        with self._lock:
            self._progress = progress

    @staticmethod
    def _bgra_to_rgb(screenshot: Any) -> np.ndarray:
        bgra = np.asarray(screenshot)
        if bgra.ndim != 3 or bgra.shape[2] < 3:
            raise RuntimeError("Captured frame must have BGRA channels.")
        if bgra.dtype != np.uint8:
            bgra = bgra.astype(np.uint8, copy=False)
        rgb = bgra[:, :, [2, 1, 0]]
        return np.ascontiguousarray(rgb)
