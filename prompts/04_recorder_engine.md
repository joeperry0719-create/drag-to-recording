# 04_recorder_engine.md

```text
Read AGENTS.md, models.py, and video_writer.py.

Implement screen_region_recorder/recorder.py.

Requirements:
- Use mss for screen capture.
- Use VideoWriter from video_writer.py.
- Run recording in a worker thread so the PySide6 UI stays responsive.
- Use threading.Event for stop control.
- Capture the selected Region at target FPS.
- Convert mss BGRA frame to RGB uint8 numpy array:
  rgb = bgra[:, :, [2, 1, 0]]
- Ensure RGB frames are C-contiguous before writing.
- Use time.perf_counter() for frame pacing.
- If the loop falls behind, avoid busy waiting.
- Always close the writer in finally.
- Expose start(config), stop(), join(timeout=None), and is_recording.
- Provide progress data: elapsed seconds, frame count, and last error if any.
- Do not call PySide widgets directly from the recording thread.
- Do not implement GUI here.

Testing:
- Add tests for thread state and stop behavior if feasible by injecting/mocking capture and writer dependencies.
- Keep tests deterministic and fast.

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. thread cleanup behavior
4. known manual tests still required
```
