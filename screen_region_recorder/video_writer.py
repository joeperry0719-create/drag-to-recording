"""MP4 video writer wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import imageio_ffmpeg
import numpy as np


class VideoWriterError(RuntimeError):
    """Raised when video writer setup or frame writing fails."""


class VideoWriter:
    """Small wrapper around imageio-ffmpeg's frame generator API."""

    def __init__(
        self,
        output_path: str | Path,
        width: int,
        height: int,
        fps: int,
        crf: int,
    ) -> None:
        if width <= 0 or height <= 0:
            raise VideoWriterError("Video width and height must be positive.")
        if width % 2 or height % 2:
            raise VideoWriterError("Video width and height must be even.")

        self.output_path = Path(output_path)
        self.width = width
        self.height = height
        self.fps = fps
        self.crf = crf
        self._writer: Any | None = None
        self._closed = False

        self._start()

    @property
    def is_closed(self) -> bool:
        return self._closed

    def _start(self) -> None:
        try:
            self._writer = imageio_ffmpeg.write_frames(
                str(self.output_path),
                (self.width, self.height),
                fps=self.fps,
                codec="libx264",
                pix_fmt_in="rgb24",
                pix_fmt_out="yuv420p",
                macro_block_size=1,
                ffmpeg_log_level="warning",
                output_params=[
                    "-crf",
                    str(self.crf),
                    "-preset",
                    "veryfast",
                    "-movflags",
                    "+faststart",
                ],
            )
            self._writer.send(None)
        except Exception as exc:
            self.close()
            raise VideoWriterError(f"Could not start MP4 writer: {exc}") from exc

    def write_frame(self, frame: np.ndarray) -> None:
        if self._closed or self._writer is None:
            raise VideoWriterError("Cannot write to a closed video writer.")
        self._validate_frame(frame)
        contiguous = np.ascontiguousarray(frame)
        try:
            self._writer.send(contiguous)
        except Exception as exc:
            raise VideoWriterError(f"Could not write video frame: {exc}") from exc

    def close(self) -> None:
        if self._closed:
            return
        writer = self._writer
        self._writer = None
        self._closed = True
        if writer is not None:
            writer.close()

    def _validate_frame(self, frame: np.ndarray) -> None:
        if not isinstance(frame, np.ndarray):
            raise VideoWriterError("Frame must be a numpy array.")
        expected_shape = (self.height, self.width, 3)
        if frame.shape != expected_shape:
            raise VideoWriterError(f"Frame shape must be {expected_shape}, got {frame.shape}.")
        if frame.dtype != np.uint8:
            raise VideoWriterError(f"Frame dtype must be uint8, got {frame.dtype}.")

    def __enter__(self) -> "VideoWriter":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
