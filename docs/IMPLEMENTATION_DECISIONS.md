# IMPLEMENTATION_DECISIONS.md

Record important implementation choices here as Codex makes them.

## Decision log template

```text
Date:
Decision:
Reason:
Alternatives considered:
Impact:
```

## Initial decisions

```text
Decision: Use PySide6 for GUI and region overlay.
Reason: Native desktop GUI support and QRubberBand for drag rectangle selection.
```

```text
Decision: Use mss for screen capture.
Reason: Lightweight cross-platform Python screenshot library with NumPy-friendly frames.
```

```text
Decision: Use imageio-ffmpeg for MP4 writer.
Reason: Direct FFmpeg frame writing without requiring OpenCV for the MVP.
```

```text
Decision: Exclude audio and cursor capture from MVP.
Reason: Reduces platform-specific complexity and allows focus on reliable region recording first.
```

```text
Date: 2026-05-04
Decision: RegionSelector returns physical capture pixels.
Reason: Qt reports logical pixels while mss capture regions use physical pixels.
Alternatives considered: Return logical pixels and let recorder scale them.
Impact: HiDPI conversion is centralized in selector.py; recorder.py passes Region directly to mss.
```

```text
Date: 2026-05-04
Decision: Poll ScreenRecorder progress from MainWindow with a QTimer.
Reason: Keeps widget updates on the GUI thread and avoids direct worker-to-widget mutation.
Alternatives considered: Emit Qt signals from a QObject worker.
Impact: Recorder remains independent of PySide6 and easier to test with fake capture/writer backends.
```
