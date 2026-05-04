# MANUAL_TEST_CHECKLIST.md

## Environment

Record these before testing:

```text
OS:
Python version:
Display count:
Display scale:
Window manager/session, if Linux:
Codex implementation commit:
```

## Basic smoke test

1. Activate virtual environment.
2. Confirm dependencies are installed with `pip install -r requirements.txt`.
3. Run `python -m screen_region_recorder.main`.
4. Confirm main window opens.
5. Confirm buttons and input fields are visible.
6. Confirm default FPS is 15 and default CRF is 23.
7. Close app normally.

Result:

```text
Pass/Fail:
Notes:
```

## Region selection test

1. Start the app.
2. Click Select Region.
3. Confirm the main window hides and the transparent overlay appears.
4. Drag top-left to bottom-right.
5. Confirm selected region appears in status label.
6. Repeat bottom-right to top-left.
7. Repeat top-right to bottom-left.
8. Repeat bottom-left to top-right.
9. Press Esc during selection and confirm no crash.
10. Try selecting an extremely small area and confirm rejection.

Result:

```text
Pass/Fail:
Notes:
```

## Recording test

1. Choose output path, for example `test_output.mp4`.
2. Set FPS to 15.
3. Set CRF to 23.
4. Select a medium-size region with visible movement.
5. Click Start Recording.
6. Confirm the main window hides before recording starts and then returns minimized.
7. Move windows or play a short animation inside the region for 5 seconds.
8. Stop using Stop Recording button.
9. Repeat once and stop using the tray menu.
10. Confirm app becomes usable again.
11. Confirm MP4 file exists.
12. Play MP4 in a video player.
13. Confirm video dimensions, colors, and content look correct.

Result:

```text
Pass/Fail:
Output file:
Notes:
```

## UI responsiveness test

1. Start recording.
2. Confirm elapsed time and frame count update while recording.
3. Try interacting with system tray or app stop control.
4. Stop recording after 10 seconds.
5. Confirm no freeze or crash.

Result:

```text
Pass/Fail:
Notes:
```

## HiDPI / scaling test

Run the region selection and recording tests at each relevant display scale:

```text
100%:
125%:
150%:
Retina / 2x:
```

Confirm the recorded area matches the selected rectangle.

## Error handling test

1. Start the app without selecting an output path.
2. Click Start Recording and confirm a user-facing error appears.
3. Choose an output path but do not select a region.
4. Click Start Recording and confirm a user-facing error appears.
5. Choose a non-`.mp4` path manually and confirm validation rejects it.

Result:

```text
Pass/Fail:
Notes:
```

## Failure report template

```text
Manual test result:
- OS:
- Display scale:
- Python version:
- Steps performed:
- Expected:
- Actual:
- Error output:
- Generated MP4 path:
- Can reproduce consistently? yes/no
```
