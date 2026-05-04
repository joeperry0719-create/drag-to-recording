# ONE_SHOT_IMPLEMENTATION_PROMPT.md

단계별 진행이 더 안전하지만, Codex에게 한 번에 MVP 초안을 만들게 하고 싶을 때만 사용하세요.

```text
Read AGENTS.md, PLAN.md, RUNBOOK.md, and docs/ACCEPTANCE_CRITERIA.md.

Implement the full MVP of Screen Region Recorder in this repository.

Required features:
- PySide6 main window
- transparent region selection overlay using QRubberBand
- Region and RecordingConfig dataclasses
- mss screen capture for selected region
- BGRA to RGB conversion
- imageio-ffmpeg MP4 writer
- worker thread recording loop
- start/stop buttons
- system tray stop action when available
- output path picker
- FPS and CRF controls
- pytest tests for pure model logic
- README and manual test checklist updates

Constraints:
- no audio
- no cursor capture
- current/primary monitor first
- no network calls
- keep UI responsive
- clean up writer in finally
- do not directly update PySide widgets from the worker thread
- hide/minimize main window before recording starts

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. how to run the app
4. known limitations
5. manual test checklist
```
