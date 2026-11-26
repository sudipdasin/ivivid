# Independent Linux release

Owner directive: do not run GitHub Actions or CircleCI without explicit approval. This branch changes automatic GitHub triggers to manual-only and disables the CircleCI workflow. External provider webhook settings and other branches are not changed.

On a clean Ubuntu 22.04/24.04 amd64 checkout, install build-essential cmake qt6-base-dev pkg-config mpv ffmpeg dpkg-dev xvfb xauth zip unzip. Run `bash packaging/build-release.sh` from the committed checkout. The script builds an isolated git archive, runs CTest, launcher, playback, spatial DSP and Xvfb smoke checks, then packages and verifies archive integrity and checksums. The output directory must not exist. SOURCE_COMMIT records the built revision. No publishing is automatic.

Before publication, independently install the DEB on clean Ubuntu VMs and test physical GPU/audio behavior as applicable. Do not overwrite an existing release with different source under the same version. Use a new version and publish only tested assets. The script is not itself a substitute for the cross-VM and installed-package checks.
