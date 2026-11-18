# iVivid testing

The Ubuntu 24.04 CI pipeline compiles C++/Qt, runs CTest (with checks active in Release builds), validates the shell launcher, parses generated mpv options, installs the actual Debian package, launches Qt offscreen, and decodes a synthetic 2-second video with audio through mpv using iVivid's filters. The media fixture is generated locally with FFmpeg and is not copyrighted.

## Local test
```sh
sudo apt install build-essential cmake qt6-base-dev mpv ffmpeg
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
bash tests/launcher_tests.sh
bash tests/playback_smoke.sh
bash packaging/build-deb.sh
sudo apt install ./dist/ivivid_0.2.0-beta.4_amd64.deb
```

## Hardware testing still required
Real Intel, AMD, NVIDIA GPU decode paths, multiple displays, HDR metadata, advanced shader performance, audio device switching, and non-Ubuntu distro packaging require independent user/hardware testing. The synthetic decode smoke test does not prove visual quality or GPU acceleration.
