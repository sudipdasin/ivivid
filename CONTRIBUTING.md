# Contributing to iVivid

Thanks for improving iVivid, a community-driven Linux video enhancement configurator.

## Getting started
Fork the repository, create a topic branch from the C++ development branch, and open a pull request. Use focused commits with clear explanations. Include test instructions, before/after behavior and screenshots for UI changes.

## Local development
Install CMake 3.20+, a C++17 compiler, Qt 6 Widgets development packages, and mpv. Run:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
cmake --build build -j2
ctest --test-dir build --output-on-failure
./build/iVivid
```

## Quality expectations
- Keep core logic testable without a graphical display.
- Avoid writing user configuration without explicit user action.
- Preserve existing settings, avoid elevated privileges and never collect personal data.
- Prefer Qt APIs over shell commands.
- Document compatibility, performance and regressions.
- Do not claim benchmarks or tests ran unless they actually ran.
- Use C++17 and follow existing formatting conventions.
- Disclose dependencies, licenses and security implications.

Open an issue for significant architectural changes before a large pull request. Contributors retain their copyright and license contributions under the repository's MIT license.
