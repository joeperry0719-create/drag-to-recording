# GOAL_PROMPT.md

아래 내용을 VS Code Codex 패널에 가장 먼저 붙여 넣으세요. 처음에는 가능하면 **Chat** 또는 **Plan** 성격으로 실행하고, Codex가 계획을 제안하게 한 뒤 다음 단계에서 Agent 모드로 구현을 맡기는 것을 권장합니다.

```text
Read AGENTS.md, PLAN.md, RUNBOOK.md, PROMPT_INDEX.md, and docs/ACCEPTANCE_CRITERIA.md.

We are building a Python desktop application called Screen Region Recorder.

Goal:
Create an MVP that lets the user select a rectangular area on the current monitor like a screenshot tool, then records that selected area over time into an MP4 video file.

Required stack:
- Python 3.11+
- PySide6 for GUI and region selection overlay
- mss for screen capture
- numpy for frame conversion
- imageio-ffmpeg for MP4 writing
- pytest for tests

MVP constraints:
- no audio recording
- no cursor capture requirement
- current/primary monitor first
- output MP4
- keep the GUI responsive while recording
- stop recording from the app or system tray
- hide or minimize the main window before recording starts
- handle resource cleanup safely

Before editing any files, produce:
1. a file-by-file implementation plan
2. the data flow from region selection to final MP4
3. the main technical risks, especially HiDPI coordinate conversion and recording thread cleanup
4. the tests you will add
5. the manual test checklist you will use

Do not edit files in this first response.
```

Codex가 계획을 제시하면 `prompts/01_models_and_tests.md`부터 순서대로 진행하세요.
