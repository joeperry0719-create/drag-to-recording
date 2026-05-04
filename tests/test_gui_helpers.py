from screen_region_recorder.main import APP_TITLE, format_elapsed
from screen_region_recorder.models import Region
from screen_region_recorder.preview_panel import format_region_origin, format_region_size
from screen_region_recorder.styles import app_stylesheet


def test_app_title_matches_reference():
    assert APP_TITLE == "Drag to recording"


def test_format_elapsed_for_status_text():
    assert format_elapsed(5.9) == "00:05"
    assert format_elapsed(65) == "01:05"
    assert format_elapsed(3661) == "01:01:01"


def test_preview_region_label_formatting():
    region = Region(320, 180, 1280, 720)

    assert format_region_origin(region) == "320, 180"
    assert format_region_size(region) == "1280 × 720"


def test_stylesheet_contains_reference_primary_color():
    stylesheet = app_stylesheet()

    assert "PrimaryButton" in stylesheet
    assert "#1f7ae8" in stylesheet
