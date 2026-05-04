# 01_models_and_tests.md

```text
Read AGENTS.md, PLAN.md, and docs/ACCEPTANCE_CRITERIA.md.

Implement the first slice only: pure models and tests.

Create or update screen_region_recorder/models.py with:
- Region dataclass: left, top, width, height
- RecordingConfig dataclass: region, output_path, fps, crf
- a function that normalizes a rectangle from two drag points
- a function or method that rejects tiny regions
- a function or method that adjusts width and height to even values for H.264/yuv420p compatibility
- validation for fps and crf
- helpful exceptions for invalid config

Requirements:
- Keep this file independent of PySide6, mss, and FFmpeg.
- Use type hints.
- Make the pure logic easy to unit test.
- Do not implement GUI, recording, or video writing yet.

Update tests/test_models.py with pytest tests covering:
- normal top-left to bottom-right drag
- reverse bottom-right to top-left drag
- top-right to bottom-left drag
- bottom-left to top-right drag
- tiny region rejection
- odd width/height adjustment
- invalid fps rejection
- invalid crf rejection

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. any assumptions you made
```
