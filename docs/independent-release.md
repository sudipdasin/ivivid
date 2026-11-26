# Independent Linux release

Owner directive: do not run GitHub Actions or CircleCI without explicit approval. This branch changes automatic GitHub triggers to manual-only and disables the CircleCI workflow. External provider webhook settings and other branches are not changed.

On a clean Ubuntu 22.04/24.04 amd64 checkout, install build-essential cmake qt6-base-dev pkg-config mpv ffmpeg dpkg-dev xvfb xauth zip unzip. Run `bash packaging/build-release.sh` from the committed checkout. The script builds an isolated git archive, runs CTest, launcher, playback, spatial DSP and Xvfb smoke checks, then packages and verifies archive integrity and checksums. The output directory must not exist. SOURCE_COMMIT records the built revision. No publishing is automatic.

Before publication, independently install the DEB on clean Ubuntu VMs and test physical GPU/audio behavior as applicable. Do not overwrite an existing release with different source under the same version. Use a new version and publish only tested assets. The script is not itself a substitute for the cross-VM and installed-package checks.

Debian metadata uses `~beta.N` for prereleases, while application versions, repository tags and asset filenames retain `-beta.N`. This lets the stable release supersede a beta under dpkg ordering. The standalone mapping test is `bash tests/debian-version-tests.sh`. A real install/upgrade test is still required.

The 2.6 integration candidate includes the signed-release roundtrip CTest and Debian version mapping gate. Sign only independently verified artifacts using an externally managed production key as described in auto-update-blueprint.md. Full native build and installed upgrade verification are mandatory before publishing.
