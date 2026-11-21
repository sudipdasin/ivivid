# v2.3.0-beta.1
- Add GUI import/export for portable mpv enhancement presets.
- Validate imported configurations before modifying GUI state; imported settings remain unsaved until explicitly applied.
- Export settings with atomic QSaveFile writes and existing validation.
- Expand GUI regression checks for both new preset controls.

# v2.3.0-beta.1
- Add local read-only media metadata inspector using ffprobe with a bounded timeout and structured JSON parsing.
- Show duration, size, codecs and video dimensions in the GUI; handle missing ffprobe and invalid files.
- Extend GUI smoke tests to assert the new inspector, diagnostics and original comparison controls exist.
- Build and publish versioned Linux executable ZIP and Debian installer after CI verification.

# v2.3.0-beta.1
- Add a read-only system diagnostics panel for Linux distribution, CPU architecture, Qt runtime, mpv availability and configuration path.
- Clarify that synchronized A/B and GPU capability probing are future work; original comparison is separate playback.
- Ship versioned executable ZIP and Debian installer with checksums after CI validation.

# v2.3.0-beta.1
- Add original-versus-enhanced playback workflow with a dedicated **Compare original…** GUI action.
- Launch original playback with `mpv --no-config -- FILE`, avoiding accidental user configuration and command-line option interpretation.
- Harden enhanced playback filename handling using `--` separator.
- Publish versioned Linux executable ZIP and Debian installer through GitHub Actions.

# v2.3.0-beta.1
- Publish a directly downloadable compiled Linux AMD64 ZIP bundle alongside the Debian installer.
- Validate ZIP integrity in Ubuntu CI and publish SHA256 checksums for both assets.
- Document host Qt6/mpv dependencies clearly; ZIP is not a self-contained AppImage.

# v2.3.0-beta.1
- Reject duplicate bass, treble and loudness-normalization stages in imported mpv audio filters.
- Add end-to-end regression tests for duplicate audio stages and preservation of saved settings.

# v2.3.0-beta.1
- Reject combined --help and --version arguments to prevent unexpected successful CLI invocations.
- Add end-to-end regression tests for malformed help/version invocations.

# v2.3.0-beta.1
- Reject unexpected or combined CLI diagnostic arguments rather than silently ignoring them.
- Add regression tests that verify invalid exports never create output files.

# v2.3.0-beta.1
- Prevent importing or exporting via symlink aliases of the active configuration.
- Add CLI regression tests verifying active settings remain unchanged on alias rejection.

# v2.3.0-beta.1
- Correct shell regression fixtures to emit actual malformed UTF-8 and embedded NUL bytes.
- Ensure oversized input fixture uses a literal NUL translation, exercising bounded import parsing.

# v2.3.0-beta.1
- Reject malformed UTF-8 and embedded NUL bytes in imported profiles.
- Add regression coverage verifying invalid text imports preserve active settings.

# v2.3.0-beta.1
- Reject imported profiles exceeding 64 KiB before parsing.
- Regression-test oversized imports and ensure existing settings remain unchanged.

# v2.3.0-beta.1
- Harden profile imports: reject unknown mpv directives and duplicate keys instead of silently ignoring them.
- Add CLI regression tests confirming invalid imports preserve active settings.

# v2.3.0-beta.1
- Add CLI profile import with strict validation and atomic installation.
- Preserve active settings when imported files are missing or invalid.
- Add VM integration tests for import/export roundtrip and rollback.

# v2.3.0-beta.1 (major-version Linux beta preview)
- Add atomic headless export of effective mpv settings to an explicit file path.
- Prevent export from overwriting active iVivid settings and reject invalid CLI arguments.
- Add export integration tests across Ubuntu VM matrix and sanitizers.
- Major beta milestone; not a production-stable release or a hardware GPU validation claim.

# v2.3.0-beta.1 (Linux beta preview)
- Add display-independent CLI diagnostics: --version, --help, --check-config, --print-config.
- Validate malformed saved settings with explicit nonzero exit status and stderr diagnostics.
- Add isolated XDG CLI integration tests to every Linux VM CTest configuration.
- Retain clipboard export, persistent settings and reset controls.

# v2.3.0-beta.1 (Linux beta preview)
- Add Copy settings to export the exact generated mpv configuration to the desktop clipboard.
- Verify clipboard output and no filesystem writes before Save using Qt GUI tests in Linux VMs.
- Retain persistent preferences, non-destructive Reset defaults, and isolated mpv configuration.

# v2.3.0-beta.1 (Linux beta preview)
- Add one-click Reset defaults without silently overwriting saved preferences.
- Verify GUI persistence across windows and reset/save behavior using VM-driven Qt tests.
- Preserve isolated mpv configuration and backward-compatible loading.

# v2.3.0-beta.1 (Linux beta preview)
- Restore last saved video and audio enhancement controls at startup.
- Validate persisted settings and reject malformed configurations without overwriting defaults.
- Add VM-backed round-trip and malformed-configuration regression tests.
- Retain Linux build, real mpv media playback, GUI interaction, and ASan/UBSan VM gates.

## [2.3.0-beta.1] — 2026-11-18
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
