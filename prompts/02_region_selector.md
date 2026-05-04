# 02_region_selector.md

```text
Read AGENTS.md and the current models.py implementation.

Implement screen_region_recorder/selector.py.

Requirements:
- Use PySide6.
- Create a full-screen transparent overlay for the current/primary screen.
- Use QRubberBand to show the selected rectangle while the user drags.
- Mouse press stores the start point.
- Mouse move updates the rubber band.
- Mouse release normalizes the selected rectangle and emits or returns a Region.
- Esc cancels selection cleanly.
- Reject regions smaller than the minimum size defined in models.py.
- Hide/close the overlay before recording can start.
- Convert Qt logical coordinates to capture coordinates carefully.
- Include comments explaining devicePixelRatio / HiDPI handling.
- Do not implement recording in this file.

API preference:
- Provide a RegionSelector class.
- Provide either a signal such as regionSelected(Region) or a small helper function that opens the selector modally and returns Optional[Region].
- Keep the public API simple for main.py.

Update docs/HIDPI_COORDINATE_NOTES.md if coordinate assumptions need to be documented.
Update README.md only if useful.

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. manual verification steps for the selector
4. any unresolved HiDPI risks
```
