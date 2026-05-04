# OS_NOTES.md

## Windows

- Use native Windows Python, not WSL, for screen capture development.
- Run VS Code and the Python process in the normal desktop session.
- Test with common display scaling values such as 100%, 125%, and 150%.
- If PowerShell blocks script execution, run commands manually or adjust execution policy according to your organization’s rules.

## macOS

- The process that runs the app may need screen recording permission.
- Depending on how you launch the app, grant permission to Terminal, VS Code, or the packaged app.
- After changing permission, restarting the app or terminal may be required.
- Test on Retina displays because logical and physical pixels can differ.

## Linux

- X11 environments are generally easier for traditional screenshot APIs.
- Wayland may restrict direct screen capture depending on compositor and portal configuration.
- If capture fails under Wayland, test under an X11 session or plan a Wayland-specific capture integration later.

## Multi-monitor note

The MVP targets current/primary monitor first. Multi-monitor support should be added after single-monitor coordinates are proven correct.
