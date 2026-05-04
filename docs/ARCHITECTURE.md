# ARCHITECTURE.md

## Component diagram

```text
+--------------------------+
| PySide6 MainWindow       |
| - output path            |
| - FPS / CRF controls     |
| - Select / Start / Stop  |
+------------+-------------+
             |
             | opens
             v
+--------------------------+
| RegionSelector           |
| - transparent overlay    |
| - QRubberBand rectangle  |
| - returns Region         |
+------------+-------------+
             |
             | Region + config
             v
+--------------------------+
| ScreenRecorder           |
| - worker thread          |
| - stop event             |
| - frame pacing           |
+------------+-------------+
             |
             | captures selected monitor area
             v
+--------------------------+
| mss                      |
| - BGRA frames            |
+------------+-------------+
             |
             | NumPy conversion BGRA -> RGB
             v
+--------------------------+
| VideoWriter              |
| - imageio-ffmpeg         |
| - MP4/H.264              |
+--------------------------+
```

## Data flow

1. User clicks **Select Region**.
2. `RegionSelector` shows a transparent full-screen overlay.
3. User drags a rectangle.
4. Selector normalizes drag coordinates and returns `Region`.
5. User chooses output path, FPS, and CRF.
6. Main window creates `RecordingConfig`.
7. Main window hides/minimizes itself and starts `ScreenRecorder`.
8. Recorder captures the selected area with `mss`.
9. Recorder converts frame from BGRA to RGB.
10. Recorder sends RGB frames to `VideoWriter`.
11. User clicks Stop or tray Stop.
12. Recorder stop event is set.
13. Writer closes in `finally`.
14. Main window shows saved path or error.

## Threading model

- PySide GUI thread owns widgets.
- Recorder worker thread owns capture loop and writer.
- Worker thread must not directly update widgets.
- `ScreenRecorder` stores `RecordingProgress` behind a lock.
- `MainWindow` uses a `QTimer` to poll progress from the GUI thread.
- Stop sets a `threading.Event`; the capture loop checks it between paced
  frames and closes the writer in `finally`.
- If screen capture falls behind the requested FPS, the recorder duplicates the
  latest captured frame to preserve real-time MP4 duration instead of producing
  a sped-up video.

## Coordinate model

The implementation distinguishes:

- Qt logical screen coordinates
- physical capture coordinates expected by mss
- selected rectangle displayed by QRubberBand

`RegionSelector` returns physical capture coordinates. It converts the selected
Qt logical rectangle once with the selected screen's `devicePixelRatio()` before
returning `Region`. `ScreenRecorder` passes that region directly to `mss`
without additional scaling.

Manual testing on scaled displays is still required, especially on mixed-DPI
multi-monitor layouts.

## Validation and cleanup

- `models.py` validates region size, FPS, CRF, and `.mp4` output paths.
- Regions are adjusted to even dimensions before encoding for H.264/yuv420p
  compatibility.
- `VideoWriter` sets `macro_block_size=1` so FFmpeg does not resize arbitrary
  even-sized capture regions to a 16-pixel boundary.
- `VideoWriter.close()` is idempotent.
- `ScreenRecorder` closes both the writer and the capture backend in `finally`.
- `main.py` reports missing region or missing output path through `QMessageBox`.
