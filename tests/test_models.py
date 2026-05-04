from pathlib import Path

import pytest

from screen_region_recorder.models import (
    RecordingConfig,
    Region,
    ValidationError,
    normalize_region,
)


def test_normalize_top_left_to_bottom_right_drag():
    assert normalize_region((10, 20), (110, 220)) == Region(10, 20, 100, 200)


def test_normalize_bottom_right_to_top_left_drag():
    assert normalize_region((110, 220), (10, 20)) == Region(10, 20, 100, 200)


def test_normalize_top_right_to_bottom_left_drag():
    assert normalize_region((110, 20), (10, 220)) == Region(10, 20, 100, 200)


def test_normalize_bottom_left_to_top_right_drag():
    assert normalize_region((10, 220), (110, 20)) == Region(10, 20, 100, 200)


def test_tiny_region_is_rejected():
    with pytest.raises(ValidationError, match="at least"):
        normalize_region((10, 10), (12, 12))


def test_odd_width_and_height_are_adjusted_to_even_values():
    region = Region(10, 20, 101, 203)

    assert region.with_even_dimensions() == Region(10, 20, 100, 202)


def test_invalid_fps_is_rejected():
    with pytest.raises(ValidationError, match="FPS"):
        RecordingConfig(
            region=Region(0, 0, 100, 100),
            output_path=Path("capture.mp4"),
            fps=0,
            crf=23,
        )


def test_invalid_crf_is_rejected():
    with pytest.raises(ValidationError, match="CRF"):
        RecordingConfig(
            region=Region(0, 0, 100, 100),
            output_path=Path("capture.mp4"),
            fps=15,
            crf=52,
        )


def test_non_mp4_output_path_is_rejected():
    with pytest.raises(ValidationError, match=".mp4"):
        RecordingConfig(
            region=Region(0, 0, 100, 100),
            output_path=Path("capture.avi"),
            fps=15,
            crf=23,
        )


def test_empty_output_path_is_rejected():
    with pytest.raises(ValidationError, match="Output path"):
        RecordingConfig(
            region=Region(0, 0, 100, 100),
            output_path="",
            fps=15,
            crf=23,
        )


def test_missing_output_directory_is_rejected():
    with pytest.raises(ValidationError, match="does not exist"):
        RecordingConfig(
            region=Region(0, 0, 100, 100),
            output_path=Path("missing-directory/capture.mp4"),
            fps=15,
            crf=23,
        )
