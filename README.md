# iVivid

**Open-source C++/Qt video and audio enhancement for Linux, powered by mpv.**

The public beta preview includes a Qt 6 GUI with separate **Video**, **Audio**, and **Experimental** tabs. Experimental features are opt-in and clearly marked.

## Install from the beta package (Ubuntu 24.04 / Debian-compatible)
Download the `ivivid_0.2.0-beta.2_amd64.deb` asset from the [GitHub Releases page](https://github.com/sudipdasin/ivivid/releases) **when the CI release workflow has succeeded**.

```sh
sudo apt install ./ivivid_0.2.0-beta.2_amd64.deb
```

Open **iVivid** from your application menu or run `iVivid`.

## Test playback
1. Select a preset in the **Video** tab.
2. Adjust audio in **Audio** and optionally enable experimental processing in **Experimental**.
3. Click **Preview settings**, then **Save settings**.
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

## Compatibility and limitations
The packaged beta targets amd64 Ubuntu 24.04. Other Linux distributions should build from source. GPU acceleration depends on hardware, drivers and mpv; feature parity with the earlier Python implementation is incomplete. Audio filters may need tuning. No source media is modified.

## Documentation and contributing
See [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), [release process](docs/RELEASING.md) and [contributor guide](CONTRIBUTING.md). MIT licensed.
