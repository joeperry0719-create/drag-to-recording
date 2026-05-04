# CODEX_USAGE_NOTES.md

## Recommended Codex workflow

1. Keep stable project guidance in `AGENTS.md`.
2. Start with a planning prompt that asks Codex not to edit files.
3. Move to Agent mode for scoped implementation slices.
4. Run tests after each slice.
5. Review diffs before moving on.
6. Use Git checkpoints so you can revert a bad change.

## Prompting style used in this package

Each implementation prompt asks Codex to:

- read relevant project guidance first
- change a narrow set of files
- avoid unrelated refactors
- run tests
- summarize changed files and assumptions

## Approval mode note

For this project, normal Agent mode is usually enough. Full Access should not be necessary for the MVP because implementation should not require network access after dependencies are installed.

## Durable instruction note

`AGENTS.md` should stay concise enough to be useful but specific enough to prevent repeated mistakes around coordinate conversion, threading, and cleanup.
