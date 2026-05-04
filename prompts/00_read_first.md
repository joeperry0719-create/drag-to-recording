# 00_read_first.md

이 폴더의 프롬프트는 VS Code Codex 패널에 **번호순으로 하나씩** 붙여 넣는 것을 전제로 작성되었습니다.

권장 모드:

- `GOAL_PROMPT.md`: Chat 또는 Plan 성격으로 실행, 파일 수정 금지
- `01` 이후: Agent 모드로 실행
- 큰 변경 전후: Git checkpoint 생성

각 프롬프트는 다음 원칙을 따릅니다.

- 한 번에 한 계층만 구현
- 테스트를 함께 추가
- `python -m pytest -q` 실행
- 변경 파일과 테스트 결과를 요약
- 실패하면 작은 수정만 수행
