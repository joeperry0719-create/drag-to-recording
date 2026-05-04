# HIDPI_COORDINATE_NOTES.md

## Problem

GUI frameworks and screen capture libraries may use different coordinate systems.

Typical risk:

- PySide6 overlay reports logical pixels.
- The capture backend expects physical pixels.
- On scaled displays, a user-selected rectangle may record the wrong area or wrong size.

## Implementation guidance for Codex

When implementing `selector.py` and `recorder.py`:

1. Identify the screen object used by the overlay.
2. Read its geometry and device pixel ratio.
3. Decide whether the returned `Region` is logical or physical.
4. Convert once, at a clearly documented boundary.
5. Avoid double scaling.
6. Add comments near the conversion code.

## MVP coordinate decision

`RegionSelector` returns `Region` in physical capture pixels. Qt mouse
positions and `QScreen.geometry()` are treated as logical pixels, then converted
once with the selected screen's `devicePixelRatio()` before the region reaches
`recorder.py`. The recorder should pass that region directly to `mss` without
additional scaling.

This is intentionally scoped to the current/primary screen for the MVP. Mixed
DPI multi-monitor layouts can need per-monitor origin handling and should be
verified manually before relying on exact capture coordinates.

## Manual verification

Use a visible target such as a browser window with a high-contrast border. Select the border tightly and record a short clip. The MP4 should match the selected rectangle.

Test with:

- Windows 100%, 125%, 150%
- macOS Retina
- external display if available
