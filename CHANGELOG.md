# v0.5.0-beta.1 (Linux beta preview)
- Add Copy settings to export the exact generated mpv configuration to the desktop clipboard.
- Verify clipboard output and no filesystem writes before Save using Qt GUI tests in Linux VMs.
- Retain persistent preferences, non-destructive Reset defaults, and isolated mpv configuration.

# v0.5.0-beta.1 (Linux beta preview)
- Add one-click Reset defaults without silently overwriting saved preferences.
- Verify GUI persistence across windows and reset/save behavior using VM-driven Qt tests.
- Preserve isolated mpv configuration and backward-compatible loading.

# v0.5.0-beta.1 (Linux beta preview)
- Restore last saved video and audio enhancement controls at startup.
- Validate persisted settings and reject malformed configurations without overwriting defaults.
- Add VM-backed round-trip and malformed-configuration regression tests.
- Retain Linux build, real mpv media playback, GUI interaction, and ASan/UBSan VM gates.

## [0.5.0-beta.1] — 2026-11-18
### Testing
- Decode generated video and audio through mpv with video and audio enhancement settings
- Verify loudness normalization independently
- Ensure C++ config assertions execute in Release builds
- Document reproducible test procedure and hardware-validation gaps

# Changelog

All notable changes to iVivid are documented here.

## [0.2.0-beta.3] — 2026-11-18
### Added
- In-app video file chooser and mpv playback test launcher
- Separate Video, Audio and Experimental tabs
- Isolated iVivid mpv configuration and Debian installer
- CI package installation, headless Qt startup and launcher smoke tests

## [0.2.0-beta.1] — 2026-11-18
### Added
- C++17 / Qt 6 desktop application preview
- CMake build and CTest configuration tests
- Range-validated mpv settings and preview
- Atomic configuration writes and one-time backup
- Architecture, contributor, roadmap and release documentation

### Known limitations
- Hardware and playback compatibility not yet validated
- Existing mpv.conf is replaced on Apply (backup made once)
- Advanced Python-era shaders and automatic GPU tier detection not yet ported
- No packaged binaries or verified release artifacts

## [1.0.0] — legacy Python project
- Original Python/Tkinter implementation (preserved on main during migration)
