# AGENTS.md

## Project mission

Build a Python desktop application that lets the user select a rectangular region on the current monitor, then records that screen region over time into an MP4 video file.

The user experience should feel similar to taking a screenshot: click **Select Region**, drag a rectangle on the screen, then click **Start Recording**. Recording should continue until the user stops it from the app or system tray.

## Operating assumptions

- Implement the MVP first.
- No audio recording in the MVP.
- No mouse cursor capture requirement in the MVP.
- Current/primary monitor support first.
- Prefer correctness, safe cleanup, and debuggability over advanced features.
- Keep the UI responsive while recording.
- Do not make network calls from the app.
- Do not add telemetry, analytics, auto-update, or hidden recording behavior.
- Do not start recording until the user explicitly clicks Start Recording.

## Tech stack

Use these technologies unless the user explicitly changes the stack:

- Python 3.11+
- PySide6 for GUI and selection overlay
- mss for screen capture
- numpy for frame conversion
- imageio-ffmpeg for MP4 writing
- pytest for tests

Do not add major dependencies without a clear reason. If a dependency is added, explain why and update `requirements.txt`, `pyproject.toml`, and README instructions.

## Repository layout

```text
screen_region_recorder/
  __init__.py
  main.py          # PySide6 application entry point
  models.py        # dataclasses and pure geometry helpers
  selector.py      # transparent region-selection overlay
  recorder.py      # recording worker and capture loop
  video_writer.py  # FFmpeg writer wrapper
tests/
  test_models.py
  test_project_imports.py
scripts/
  setup_windows.ps1
  setup_unix.sh
  run_tests.ps1
  run_tests.sh
docs/
  ARCHITECTURE.md
  ACCEPTANCE_CRITERIA.md
  MANUAL_TEST_CHECKLIST.md
  OS_NOTES.md
  TROUBLESHOOTING.md
prompts/
  numbered Codex prompts
```

## Implementation rules

### General

- Keep functions small and testable.
- Put pure logic in `models.py` where possible.
- Use clear error messages for the user.
- Prefer explicit types and dataclasses.
- Make resource cleanup deterministic with `try/finally`.
- Avoid global mutable state except for the QApplication lifecycle.

### Screen coordinates

- Be careful with HiDPI and display scaling.
- Qt may report logical pixels while screen capture libraries may expect physical pixels.
- Comment all coordinate conversions.
- Test dragging in all directions:
  - top-left to bottom-right
  - bottom-right to top-left
  - top-right to bottom-left
  - bottom-left to top-right
- Reject tiny regions below the configured minimum size.
- Ensure encoded width and height are positive and even.

### Video encoding

- Use `imageio_ffmpeg.write_frames` through a small wrapper class.
- Feed RGB uint8 frames shaped `(height, width, 3)`.
- Convert mss BGRA frames to RGB with channel reordering.
- Ensure frames are C-contiguous before sending to FFmpeg.
- Use MP4-compatible output settings, including `pix_fmt_out="yuv420p"`.
- Close the writer in `finally`, even on exceptions.

### Threading

- The recording loop must not run on the PySide GUI thread.
- Use a worker thread and a stop event.
- Do not directly mutate PySide widgets from worker threads.
- Surface progress through safe callbacks, signals, or polling.
- Stop recording safely even if the writer or capture loop raises an exception.

### GUI

- Main window fields:
  - output file picker
  - FPS spinbox, default 15, range 1 to 60
  - CRF/quality field, default 23
  - Select Region button
  - Start Recording button
  - Stop Recording button
  - status label
- Main window should hide or minimize before recording starts so it does not accidentally appear in the capture region.
- Provide a system tray icon with a Stop Recording action when supported.
- Use QMessageBox for user-facing errors.

## Commands

Run tests:

```bash
python -m pytest -q
```

Compile check:

```bash
python -m compileall screen_region_recorder
```

Run app:

```bash
python -m screen_region_recorder.main
```

## Testing expectations

At minimum, add tests for:

- rectangle normalization
- reverse drag
- tiny region rejection
- odd dimension adjustment
- invalid FPS rejection
- basic package import

GUI and recording behavior will need manual tests. Keep manual test steps in `docs/MANUAL_TEST_CHECKLIST.md` updated.

## Git and change management

- Do not commit unless explicitly instructed by the user.
- After each step, summarize changed files and test results.
- Keep changes scoped to the current prompt.
- If a prompt asks for planning only, do not edit files.
- If tests fail, fix high-confidence issues before proceeding.

## Completion criteria for MVP

The MVP is complete when:

1. The user can select a rectangular screen region.
2. The selected region is displayed in the main UI.
3. The user can choose an MP4 output path.
4. The user can start and stop recording.
5. The app remains responsive while recording.
6. The output MP4 plays in a normal video player.
7. `python -m pytest -q` passes.
8. Known limitations are documented.
