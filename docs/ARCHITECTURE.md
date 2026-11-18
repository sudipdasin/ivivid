# iVivid C++ architecture

The application uses Qt 6 Widgets for its GUI, with separate Video, Audio and Experimental tabs. Config serialization is implemented in `src/Config.cpp` and validated by `tests/config_tests.cpp`.

## Non-destructive integration
iVivid writes only `~/.config/iVivid/mpv.conf` via QSaveFile. It does not overwrite the user's normal `~/.config/mpv/mpv.conf`. The `ivivid-play` launcher invokes mpv with `--include` to load iVivid's generated settings alongside regular mpv settings. No elevated privileges are needed to use the GUI.

## Packaging
CMake installs the executable, launcher and desktop entry. CI compiles on Ubuntu 24.04, runs CTest and builds an amd64 Debian package. Package compatibility beyond the CI distro is not guaranteed.

## Boundaries
The application configures playback rather than modifying source media. Hardware decode is best-effort. The experimental tab is opt-in; additional shaders and capability detection are future development.
