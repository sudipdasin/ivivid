# v1.1.1-beta.1
- Harden profile imports: reject unknown mpv directives and duplicate keys instead of silently ignoring them.
- Add CLI regression tests confirming invalid imports preserve active settings.

# v1.1.1-beta.1
- Add CLI profile import with strict validation and atomic installation.
- Preserve active settings when imported files are missing or invalid.
- Add VM integration tests for import/export roundtrip and rollback.

# v1.1.1-beta.1 (major-version Linux beta preview)
- Add atomic headless export of effective mpv settings to an explicit file path.
- Prevent export from overwriting active iVivid settings and reject invalid CLI arguments.
- Add export integration tests across Ubuntu VM matrix and sanitizers.
- Major beta milestone; not a production-stable release or a hardware GPU validation claim.

# v1.1.1-beta.1 (Linux beta preview)
- Add display-independent CLI diagnostics: --version, --help, --check-config, --print-config.
- Validate malformed saved settings with explicit nonzero exit status and stderr diagnostics.
- Add isolated XDG CLI integration tests to every Linux VM CTest configuration.
- Retain clipboard export, persistent settings and reset controls.

# v1.1.1-beta.1 (Linux beta preview)
- Add Copy settings to export the exact generated mpv configuration to the desktop clipboard.
- Verify clipboard output and no filesystem writes before Save using Qt GUI tests in Linux VMs.
- Retain persistent preferences, non-destructive Reset defaults, and isolated mpv configuration.

# v1.1.1-beta.1 (Linux beta preview)
- Add one-click Reset defaults without silently overwriting saved preferences.
- Verify GUI persistence across windows and reset/save behavior using VM-driven Qt tests.
- Preserve isolated mpv configuration and backward-compatible loading.

# v1.1.1-beta.1 (Linux beta preview)
- Restore last saved video and audio enhancement controls at startup.
- Validate persisted settings and reject malformed configurations without overwriting defaults.
- Add VM-backed round-trip and malformed-configuration regression tests.
- Retain Linux build, real mpv media playback, GUI interaction, and ASan/UBSan VM gates.

## [1.1.1-beta.1] — 2026-11-18
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
