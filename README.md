# iVivid

**Modern Linux video and audio enhancement, powered by mpv.**

iVivid is an open-source desktop configurator for mpv. The C++ beta preview replaces the original Python/Tkinter application with a Qt 6 interface and a testable configuration engine. It adjusts playback settings; it does not alter source media files.

> **Status: v0.2.0-beta.1 source preview — not hardware-validated.** The previous Python implementation remains on `main` during migration.

## Features in this preview
- Professional dark Qt interface with Light, Balanced and Max presets
- Saturation, brightness, contrast, debanding and safe hardware decoding controls
- Bass and treble boosts, optional loudness normalization
- Live text preview of the generated mpv configuration
- Validation, atomic writes and a one-time backup of an existing mpv.conf
- No root privileges, no Python runtime

## Requirements
Linux, C++17 compiler, CMake 3.20+, Qt 6.2 Widgets development package, mpv (for playback).

Debian/Ubuntu example:
```sh
sudo apt install build-essential cmake qt6-base-dev mpv
```

## Build and run
```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build -j2
ctest --test-dir build --output-on-failure
./build/iVivid
```

Choose a preset, preview the resulting configuration, then click **Apply to mpv**. Restart mpv playback to use the new settings.

**Important:** Apply currently replaces `~/.config/mpv/mpv.conf`. A first-write backup is saved as `mpv.conf.ivivid-backup` if a configuration already exists. If you use custom mpv settings, make a separate backup before applying. A safer non-destructive profile-based approach is planned.

## Documentation
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Release checklist](docs/RELEASING.md)
- [Contributing](CONTRIBUTING.md)

## License
MIT. See [LICENSE](LICENSE).

## Contributing
Bug reports, testing across distributions, accessibility improvements, shader compatibility work and performance benchmarks are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md).
