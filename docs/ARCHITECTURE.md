# iVivid architecture (C++ beta preview)

iVivid is a Qt 6 Widgets desktop application. It does not modify video files. It generates a user-level mpv configuration for playback enhancement.

- `src/main.cpp`: Qt application startup.
- `src/MainWindow.*`: presentation, controls and user feedback.
- `src/Config.*`: validated settings, mpv serialization and atomic persistence.
- `tests/`: isolated configuration unit tests.

## Safety model
No root privileges are required. Settings are range-validated before serialization. The first preexisting `~/.config/mpv/mpv.conf` is copied to `mpv.conf.ivivid-backup`. Writes use `QSaveFile` for atomic replacement. **Important:** applying iVivid replaces the active mpv.conf, so users with complex configurations should review the preview and backup first.

## Design boundaries
Qt owns UI only; config logic is separately testable. mpv remains the playback engine. A future iteration should merge or use an isolated profile instead of replacing the entire config, and introduce capability detection, profile import/export, shader availability checks and diagnostics.

## Compatibility
Qt 6.2+, C++17, CMake 3.20+, mpv in PATH. Hardware decoding depends on driver support and mpv's platform-specific backend; not guaranteed by this application.
