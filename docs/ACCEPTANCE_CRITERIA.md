# ACCEPTANCE_CRITERIA.md

## MVP acceptance criteria

The project is acceptable when all of the following are true.

### Basic app behavior

- `python -m screen_region_recorder.main` starts the app.
- The main window has output path, FPS, CRF, Select Region, Start Recording, Stop Recording, and status UI.
- The app handles missing output path with a user-facing error.
- The app handles missing selected region with a user-facing error.

### Region selection

- User can drag a rectangular region on the current/primary screen.
- Dragging in any direction creates the correct normalized region.
- Very small regions are rejected.
- Esc cancels selection without crashing.
- The overlay disappears before recording starts.

### Recording

- Start Recording begins capture without freezing the GUI.
- Stop Recording stops the worker thread safely.
- The writer closes even if recording is stopped early.
- An MP4 file is produced at the selected path.
- The MP4 plays in a normal video player.
- Captured colors look correct.

### Tests and code quality

- `python -m pytest -q` passes.
- `python -m compileall screen_region_recorder` passes.
- Pure geometry and validation logic are unit tested.
- Recording thread does not directly mutate PySide widgets.
- Resource cleanup uses `try/finally`.

### Documented limitations

README or docs must state:

- no audio in MVP
- no cursor capture in MVP
- current/primary monitor first
- HiDPI scaling requires manual verification
- Linux Wayland may require special handling
- macOS may require screen recording permission
