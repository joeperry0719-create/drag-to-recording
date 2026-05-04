# RUNBOOK.md — 실제 실행 순서

## 1. ZIP 압축 해제 후 VS Code 열기

```bash
cd screen-region-recorder-codex-plan-package
code .
```

## 2. 가상환경 생성

### Windows PowerShell

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

## 3. Git 초기화

```bash
git init
git add .
git commit -m "Initialize screen region recorder Codex package"
```

## 4. Codex 첫 실행

VS Code Codex 패널에서 `GOAL_PROMPT.md` 내용을 붙여 넣습니다.

첫 프롬프트는 계획 수립만 요청합니다. Codex가 바로 파일을 수정하지 않게 되어 있습니다.

## 5. 단계별 구현

아래 순서로 `prompts/` 파일 내용을 Codex에 하나씩 붙여 넣습니다.

```text
01_models_and_tests.md
02_region_selector.md
03_video_writer.md
04_recorder_engine.md
05_main_gui.md
06_docs_and_readme.md
07_manual_test_debug.md
08_pr_review_hardening.md
```

각 단계가 끝나면 아래 명령을 실행합니다.

```bash
python -m pytest -q
python -m compileall screen_region_recorder
```

문제가 없으면 checkpoint를 남깁니다.

```bash
git status
git diff --stat
git add .
git commit -m "Complete <phase name>"
```

## 6. 최종 앱 실행

```bash
python -m screen_region_recorder.main
```

## 7. 실패 시 복구 방법

가장 최근 변경사항을 폐기하려면:

```bash
git restore .
```

마지막 commit으로 되돌리려면:

```bash
git reset --hard HEAD
```

특정 단계의 diff만 보고 싶으면:

```bash
git diff
```

## 8. Codex에게 오류 수정 요청 시 템플릿

```text
The latest implementation failed this command:
python -m pytest -q

Here is the error output:
<paste error>

Fix the smallest high-confidence issue only.
Do not redesign the architecture.
After fixing, run:
python -m pytest -q
python -m compileall screen_region_recorder
Summarize changed files and the root cause.
```
