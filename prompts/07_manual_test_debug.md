# 07_manual_test_debug.md

```text
We are now doing manual integration testing.

First, inspect the current implementation and list the exact manual test steps for this OS.
Then wait for the user to paste the manual test result.

When the user provides the result, fix only high-confidence bugs related to:
- region coordinate mismatch
- HiDPI scaling
- app window appearing in the recording
- failure to create MP4
- stop button not stopping recording
- UI freezing
- wrong colors due to BGRA/RGB conversion

After any fix, run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. root cause
2. changed files
3. test result
4. next manual test to repeat
```

수동 테스트 결과를 Codex에 줄 때는 아래 템플릿을 사용하세요.

```text
Manual test result:
- OS:
- Display scale:
- Python version:
- Steps performed:
- Expected:
- Actual:
- Error output or screenshot description:
- Generated MP4 path, if any:
```
