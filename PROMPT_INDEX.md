# PROMPT_INDEX.md

| 순서 | 파일 | 목적 | 예상 변경 파일 | 완료 기준 |
|---:|---|---|---|---|
| 0 | `GOAL_PROMPT.md` | 전체 계획 확인 | 없음 | Codex가 계획만 제시 |
| 1 | `prompts/01_models_and_tests.md` | dataclass와 순수 로직 | `models.py`, `tests/test_models.py` | pytest 통과 |
| 2 | `prompts/02_region_selector.md` | 화면 영역 선택 overlay | `selector.py`, README/docs 일부 | 선택 영역 반환 |
| 3 | `prompts/03_video_writer.md` | MP4 writer wrapper | `video_writer.py`, tests | frame validation |
| 4 | `prompts/04_recorder_engine.md` | mss 캡처 worker | `recorder.py` | stop/cleanup 안전 |
| 5 | `prompts/05_main_gui.md` | GUI 통합 | `main.py` | 앱 실행 가능 |
| 6 | `prompts/06_docs_and_readme.md` | 문서 정리 | README, docs | 설치/실행 안내 완성 |
| 7 | `prompts/07_manual_test_debug.md` | 수동 테스트 후 수정 | 필요한 파일 | 실제 MP4 녹화 확인 |
| 8 | `prompts/08_pr_review_hardening.md` | PR 리뷰식 하드닝 | 필요한 파일 | 고신뢰 버그 수정 |

## 권장 commit 메시지

```bash
git commit -m "Add region models and tests"
git commit -m "Add screen region selector overlay"
git commit -m "Add MP4 video writer"
git commit -m "Add screen recorder engine"
git commit -m "Add PySide6 main GUI"
git commit -m "Finalize docs and manual test checklist"
git commit -m "Harden MVP after review"
```
