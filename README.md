# iVivid

> **Current AppVeyor build preview (2026-11-28):** [Setup, source checkpoint, test evidence and release gates](docs/APPVEYOR_BUILD_PREVIEW.md). This isolated Qt6 2.6 beta build configuration has passed 14 local wrapper fixtures; no hosted native package or installed acceptance yet. Historical CI/release instructions below are not authorization to execute GitHub Actions or CircleCI. No paid services.


**Open-source C++/Qt video and audio enhancement for Linux, powered by mpv.**

The public beta preview includes a Qt 6 GUI with separate **Video**, **Audio**, and **Experimental** tabs. Experimental features are opt-in and clearly marked.

## Install from the beta package (Ubuntu 24.04 / Debian-compatible)
Download the `ivivid_2.5.0-beta.1_amd64.deb` asset from the [GitHub Releases page](https://github.com/sudipdasin/ivivid/releases) **when the CI release workflow has succeeded**.

```sh
sudo apt install ./ivivid_2.5.0-beta.1_amd64.deb
```

Open **iVivid** from your application menu or run `iVivid`.

## Headless diagnostics
Run `iVivid --version`, `iVivid --help`, `iVivid --check-config`, `iVivid --print-config`, or `iVivid --export-config /path/to/export.conf`, or `iVivid --import-config /path/to/export.conf` from a terminal or CI VM without a graphical display. Invalid saved configurations return exit status 2.

## Test playback
1. Select a preset in the **Video** tab.
2. Adjust audio in **Audio** and optionally enable experimental processing in **Experimental**.
3. Click **Preview settings**, then **Save settings**. Use **Copy settings** to inspect or share the generated mpv configuration. Use **Reset defaults** to restore initial controls without changing the saved file until you save again. You can also click **Test video…** to select a local file and launch mpv.
4. Play a local video:
   ```sh
   ivivid-play /path/to/video.mp4
   ```

The wrapper launches mpv with an iVivid-specific configuration. Your existing `~/.config/mpv/mpv.conf` is not overwritten.

## Build from source
Requirements: Linux, C++17 compiler, CMake 3.20+, Qt 6.2 Widgets, mpv.
```sh
sudo apt install build-essential cmake qt6-base-dev mpv
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
./build/iVivid
```
For a source-tree playback test, use `scripts/ivivid-play /path/to/video.mp4`.

## Verification

CI includes real decoding of a synthetic video/audio file using mpv filters. See [testing](docs/TESTING.md) for reproduction and hardware-test gaps.

## Compatibility and limitations
The packaged beta targets amd64 Ubuntu 24.04. Other Linux distributions should build from source. GPU acceleration depends on hardware, drivers and mpv; feature parity with the earlier Python implementation is incomplete. Audio filters may need tuning. No source media is modified.

## Documentation and contributing
See [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), [release process](docs/RELEASING.md) and [contributor guide](CONTRIBUTING.md). MIT licensed.


### Downloadable Linux ZIP bundle
The GitHub Releases page also offers `ivivid-2.5.0-beta.1-linux-amd64.zip`, containing the compiled `bin/iVivid` executable and launcher. It requires host Qt6 Widgets and mpv; it is **not** a fully self-contained AppImage. The Debian `.deb` remains recommended for Ubuntu/Debian systems.


### Compare original playback (v2 beta)
Use **Compare original…** to launch mpv with `--no-config`, bypassing iVivid enhancements and user mpv configuration. Use **Test video…** for enhanced playback with the saved iVivid settings. These are separate player windows rather than synchronized A/B frames. Both commands pass `--` before the selected filename to prevent option interpretation.


### System diagnostics (v2.1 beta)
The GUI includes a **System diagnostics** button displaying the detected operating system, CPU architecture, Qt runtime version, mpv executable path, and iVivid configuration location and existence. This is a local read-only report; it does not probe GPU acceleration or upload data.


### Inspect media metadata (v2.2 beta)
Click **Inspect media…** to view local media duration, file size, codec names, and video resolution using `ffprobe` (from FFmpeg). The operation is read-only, has a ten-second timeout, and displays metadata locally. It does not decode, edit, or upload media.


### Portable preset import/export (v2.3 beta)
The GUI can export the currently selected settings to a standalone mpv `.conf` preset with an atomic file write. **Import preset…** validates the selected configuration using the existing strict parser before updating the controls. Import does not overwrite saved iVivid settings until the user explicitly clicks **Save settings**.


### Workflow layout and keyboard shortcuts (v2.4 beta)
The primary controls are now grouped into three rows—preset management, tools, and playback/save—rather than a single overflowing toolbar. Keyboard shortcuts: **Ctrl+S** saves enhancements, **Ctrl+O** imports a preset, and **Ctrl+P** previews generated settings.


### 3D Spatial Sound (v2.5 beta)
Enable **3D Spatial Sound — stereo widening (headphones)** in the Audio tab. The optional effect uses FFmpeg's `stereowiden` filter through mpv (`delay=20`, `feedback=0.3`, `crossfeed=0.3`, `drymix=0.8`). It expands stereo width but **does not** provide discrete multichannel surround, head tracking, or true binaural 3D positioning. The effect is disabled by default and may affect mono compatibility; compare with the original before enabling for extended listening. Import/export and saved settings preserve the toggle.


### Repository update discovery (2.6 candidate)
The Software updates panel checks GitHub releases automatically on startup and every six hours while running, or on demand. Choose Stable or Beta and disable automatic checks if desired. The helper matches amd64 DEB or ZIP assets and a checksum file, rejects downgrades, and does not install anything. Manual release downloads remain available; signed package authentication and automatic installation/rollback are not yet implemented. Python 3 is required. `IVIVID_DISABLE_UPDATE_CHECK=1` disables network checks for tests or offline sessions.
