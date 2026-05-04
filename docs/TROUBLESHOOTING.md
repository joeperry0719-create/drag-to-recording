# TROUBLESHOOTING.md

## `ModuleNotFoundError: No module named 'PySide6'`

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

On Windows, make sure this command runs in native Windows Python rather than
WSL.

## `No module named pytest`

Install the test dependency in the active virtual environment:

```bash
pip install -r requirements.txt
```

`pytest` is listed in `requirements.txt` and in the `dev` optional dependencies
in `pyproject.toml`.

## App does not start after clicking Start Recording

Check the user-facing message. Common validation failures:

- no output path selected
- no region selected
- output path does not end in `.mp4`
- region is too small

## App starts but screen capture is black or empty

Possible causes:

- macOS screen recording permission not granted
- Linux Wayland restrictions
- running inside a remote/virtual desktop session
- running from WSL instead of native Windows Python

The recorder uses `mss.MSS` as the default capture backend.

## Output MP4 does not play

Possible causes:

- writer was not closed
- app crashed before `close()`
- odd frame dimensions with incompatible pixel format
- FFmpeg codec issue
- output directory does not exist or is not writable

Ask Codex to inspect `VideoWriter.close()` and the recorder `finally` block.

## Output MP4 is shorter than the recording time

This means the capture loop fell behind the requested FPS but the writer still
encoded the available frames at the requested FPS. The recorder should duplicate
the latest captured frame when needed so MP4 duration follows elapsed wall-clock
time. Ask Codex to inspect `ScreenRecorder._run()` frame pacing.

## Colors look wrong

Likely BGRA/RGB conversion issue.

Expected conversion from mss frame array:

```python
rgb = bgra[:, :, [2, 1, 0]]
```

## Recorded area is offset or scaled incorrectly

Likely HiDPI coordinate mismatch.

Ask Codex to review:

- `selector.py` device pixel ratio handling
- screen geometry offsets
- whether coordinates are logical or physical
- multi-monitor assumptions

## Stop button does not stop recording

Likely thread stop event or GUI-thread blocking issue.

Ask Codex to review:

- whether recording loop runs on worker thread
- whether stop event is checked every frame
- whether writer close blocks indefinitely
- whether GUI event loop remains active

The current implementation stops by setting a `threading.Event` and polling
recorder state from `MainWindow` with a `QTimer`. The GUI thread should not run
the capture loop directly.
