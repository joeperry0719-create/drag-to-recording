# QUALITY_BAR.md

## Must-have quality bar

- No hidden recording.
- No network calls from the app.
- Recording starts only after explicit user action.
- GUI remains responsive.
- Recorder thread stops safely.
- Writer closes in all normal and error paths.
- Selected region is validated before recording.
- Output dimensions are positive and even.
- User-facing errors are understandable.
- Tests cover pure geometry and validation logic.

## Nice-to-have quality bar

- Progress display for elapsed time and frame count.
- Tray action for Stop Recording.
- Helpful troubleshooting messages.
- Manual test checklist updated after real testing.
- Clear comments around HiDPI behavior.
