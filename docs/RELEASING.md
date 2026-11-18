# Release process

Use semantic versioning. Previews use tags such as `v0.2.0-beta.1`.

Before publishing a binary release:
1. Build on clean supported Linux environments.
2. Run `ctest --output-on-failure`.
3. Test mpv 0.39+ on Intel and AMD hardware.
4. Verify backup/restore and existing configuration preservation.
5. Check accessibility and desktop integration.
6. Document known limitations and supply checksums for artifacts.
7. Review licenses and dependencies.

The initial C++ preview is source-only and **not hardware-validated**. Do not describe it as a tested stable release.
