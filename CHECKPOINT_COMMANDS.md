# CHECKPOINT_COMMANDS.md

## Initial checkpoint

```bash
git init
git add .
git commit -m "Initialize screen region recorder Codex package"
```

## After each Codex phase

```bash
python -m pytest -q
python -m compileall screen_region_recorder
git status
git diff --stat
git add .
git commit -m "Complete <phase name>"
```

## Inspect changes

```bash
git diff
git diff --stat
git status
```

## Revert uncommitted changes

```bash
git restore .
```

## Return to last commit

```bash
git reset --hard HEAD
```
