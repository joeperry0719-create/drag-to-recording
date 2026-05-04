# 05_main_gui.md

```text
Read AGENTS.md, selector.py, recorder.py, models.py, and video_writer.py.

Implement screen_region_recorder/main.py.

Requirements:
- Build a PySide6 main window.
- Provide UI fields:
  - output file picker
  - FPS spinbox, default 15, range 1 to 60
  - CRF spinbox or field, default 23, range 0 to 51
  - Select Region button
  - Start Recording button
  - Stop Recording button
  - status label showing selected region, elapsed time, frame count, and saved path
- When Select Region is clicked, open RegionSelector and store the returned Region.
- Start Recording should:
  - validate output path
  - validate selected region
  - create RecordingConfig
  - hide or minimize the main window before recording starts
  - start ScreenRecorder
  - show a system tray icon with Stop Recording action when available
- Stop Recording should:
  - stop ScreenRecorder safely
  - wait briefly for cleanup without freezing the UI
  - show the main window again
  - update status with saved path or error
- Handle user-facing errors with QMessageBox.
- Add a QApplication entry point so this command works:
  python -m screen_region_recorder.main
- Do not block the GUI thread with a long recording loop.

Add or update README usage instructions if needed.

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. how to run the app
4. manual GUI test steps
```
