# Drag to recording

Drag to recording is a Python desktop MVP for selecting a rectangular area
on the current or primary monitor and recording that area to an MP4 file.

The MVP uses PySide6 for the GUI and selection overlay, mss for screen capture,
NumPy for frame conversion, and imageio-ffmpeg for MP4 writing. It does not
record audio or require cursor capture.

## Install

### Windows PowerShell

Use native Windows Python, not WSL, for screen capture.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python -m screen_region_recorder.main
```

## Windows Executable

Download the Windows executable bundle from the GitHub Releases page:

```text
https://github.com/joeperry0719-create/drag-to-recording/releases
```

Download `Drag-to-recording-windows-x64.zip`, extract it, then run:

```text
Drag to recording/Drag to recording.exe
```

Keep the whole extracted `Drag to recording` folder together. The `.exe`
depends on the bundled `_internal` folder next to it.

When building locally, the packaged Windows build is created as an onedir app:

```text
dist_exe/Drag to recording/Drag to recording.exe
```

To rebuild the executable from this repository:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist_exe --workpath build_exe "packaging\Drag to recording.spec"
```

## Usage

1. Confirm the window title is **Drag to recording**.
2. Choose an `.mp4` output path.
3. Set FPS. The default is 15; the supported range is 1 to 60.
4. Set CRF quality. The default is 23; lower values are higher quality.
5. Click **Select Region**.
6. Drag a rectangle on the current or primary monitor.
7. Click **Start Recording**.
8. Stop recording from the app button or the system tray menu.
9. Open the saved MP4 in a normal video player.

The main window hides before recording starts and then returns minimized, so it
is less likely to appear in the captured region while still being reachable from
the taskbar.

## Development Checks

```bash
python -m pytest -q
python -m compileall screen_region_recorder
```

If `pytest`, PySide6, mss, NumPy, or imageio-ffmpeg are missing, activate the
virtual environment and install `requirements.txt`.

## Troubleshooting

- `ModuleNotFoundError: No module named 'PySide6'`: install dependencies from
  `requirements.txt` in the active environment.
- `No module named pytest`: install development dependencies or use
  `pip install -r requirements.txt pytest`.
- Black or empty capture: macOS permissions, Linux Wayland restrictions, remote
  desktop sessions, and WSL can block screen capture.
- Output MP4 does not play: confirm the writer closed cleanly and that the
  output path is writable.
- Wrong colors: inspect the BGRA to RGB conversion in `recorder.py`.
- Offset or scaled recording area: repeat the HiDPI checklist in
  `docs/HIDPI_COORDINATE_NOTES.md`.

## Platform Notes

macOS may require Screen Recording permission for the app launcher, Terminal, or
VS Code. Restart the process after changing the permission.

Linux Wayland may restrict direct screen capture. Test under X11 if capture is
black or unavailable.

## Manual Visual QA Checklist

1. Launch the app.
2. Confirm the main window title is **Drag to recording**.
3. Confirm the layout visually matches
   `assets/ui_reference/drag_to_recording_reference.png`.
4. Click **Browse** and choose an MP4 path.
5. Click **Select Region** and drag a rectangle.
6. Confirm Left, Top, Width, and Height update.
7. Click **Start Recording**.
8. Confirm Start disables and Stop enables.
9. Record 5 seconds.
10. Click **Stop Recording**.
11. Confirm the MP4 file exists and plays.
12. Confirm the app can close without hanging.

## Known Limitations

- No audio recording in the MVP.
- The visible **Show cursor** option is disabled because cursor capture is not
  implemented in the MVP.
- Current or primary monitor support first.
- HiDPI scaling requires manual verification.
- Mixed-DPI multi-monitor setups are not fully handled yet.
- The app does not make network calls, does not include telemetry, and does not
  start recording until the user explicitly clicks **Start Recording**.
