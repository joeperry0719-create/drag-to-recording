# COPY_TO_EXISTING_REPO.md

If you already have a repository and only want the Codex execution package:

1. Copy these files into the repository root:

```text
AGENTS.md
agent.md
GOAL_PROMPT.md
PLAN.md
RUNBOOK.md
PROMPT_INDEX.md
prompts/
docs/
scripts/
CHECKPOINT_COMMANDS.md
TASKS.md
```

2. If your repo already has source files, do not overwrite them blindly.
3. Ask Codex to inspect the existing structure and adapt the plan.

Use this prompt:

```text
Read AGENTS.md, PLAN.md, and the existing repository.
Adapt the Screen Region Recorder implementation plan to the current file layout.
Do not edit files yet. Return a migration-safe plan first.
```
