"""Data models and pure geometry helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import SupportsInt


MIN_REGION_SIZE = 10
MIN_FPS = 1
MAX_FPS = 60
MIN_CRF = 0
MAX_CRF = 51


class ValidationError(ValueError):
    """Raised when user supplied recording settings are invalid."""


@dataclass(frozen=True)
class Region:
    """A screen capture region in physical capture pixels."""

    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def validate(self, min_size: int = MIN_REGION_SIZE) -> "Region":
        if self.width <= 0 or self.height <= 0:
            raise ValidationError("Region width and height must be positive.")
        if self.width < min_size or self.height < min_size:
            raise ValidationError(
                f"Region must be at least {min_size}x{min_size} pixels."
            )
        return self

    def with_even_dimensions(self) -> "Region":
        """Return a region with dimensions compatible with H.264 yuv420p output."""

        width = self.width - (self.width % 2)
        height = self.height - (self.height % 2)
        if width <= 0 or height <= 0:
            raise ValidationError("Region is too small after even-dimension adjustment.")
        return Region(self.left, self.top, width, height)

    def as_mss_monitor(self) -> dict[str, int]:
        """Return the dictionary shape expected by mss.grab()."""

        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True)
class RecordingConfig:
    """Validated settings needed by the recording worker."""

    region: Region
    output_path: Path
    fps: int = 15
    crf: int = 23

    def __post_init__(self) -> None:
        raw_output_path = self.output_path
        if raw_output_path is None or not str(raw_output_path).strip():
            raise ValidationError("Output path is required.")
        object.__setattr__(self, "output_path", Path(self.output_path))
        self.region.validate().with_even_dimensions()
        validate_fps(self.fps)
        validate_crf(self.crf)
        if self.output_path.suffix.lower() != ".mp4":
            raise ValidationError("Output path must use the .mp4 extension.")
        if self.output_path.parent and not self.output_path.parent.exists():
            raise ValidationError(f"Output directory does not exist: {self.output_path.parent}")

    @property
    def encoder_region(self) -> Region:
        return self.region.with_even_dimensions()


def normalize_region(
    start: tuple[SupportsInt, SupportsInt],
    end: tuple[SupportsInt, SupportsInt],
    *,
    min_size: int = MIN_REGION_SIZE,
) -> Region:
    """Create a normalized capture region from two drag endpoints."""

    start_x, start_y = int(start[0]), int(start[1])
    end_x, end_y = int(end[0]), int(end[1])
    left = min(start_x, end_x)
    top = min(start_y, end_y)
    width = abs(end_x - start_x)
    height = abs(end_y - start_y)
    return Region(left, top, width, height).validate(min_size)


def validate_fps(fps: int) -> int:
    if not isinstance(fps, int):
        raise ValidationError("FPS must be an integer.")
    if fps < MIN_FPS or fps > MAX_FPS:
        raise ValidationError(f"FPS must be between {MIN_FPS} and {MAX_FPS}.")
    return fps


def validate_crf(crf: int) -> int:
    if not isinstance(crf, int):
        raise ValidationError("CRF must be an integer.")
    if crf < MIN_CRF or crf > MAX_CRF:
        raise ValidationError(f"CRF must be between {MIN_CRF} and {MAX_CRF}.")
    return crf
