# SECURITY_AND_PRIVACY.md

## Privacy expectations

A screen recorder can capture sensitive information. The MVP should follow these rules:

- Do not record until the user explicitly starts recording.
- Make recording state visible in the UI or tray.
- Store video only at the user-selected output path.
- Do not upload recordings.
- Do not add analytics or telemetry.
- Do not persist selected regions unless explicitly added as a future feature.

## Safe implementation practices

- Keep file writes limited to the selected output video path and normal logs if logs are added later.
- Do not request unnecessary OS permissions.
- Avoid background services or auto-start behavior.
- Make stop behavior reliable.
