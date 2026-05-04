# 08_pr_review_hardening.md

```text
Review the current implementation as if you are doing a PR review.

Focus on:
- coordinate correctness
- HiDPI scaling
- frame color conversion BGRA -> RGB
- recording thread stop behavior
- VideoWriter cleanup
- UI responsiveness
- whether the selection overlay or main window can be accidentally captured
- output path validation
- user-facing error messages
- tests that are brittle or missing

Then:
1. List issues by severity: critical, high, medium, low.
2. Fix only critical/high issues that you are confident about.
3. Do not redesign the entire app.
4. Run:
   python -m pytest -q
   python -m compileall screen_region_recorder
5. Summarize the final diff.
```
