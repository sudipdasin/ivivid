#!/bin/bash
# fix-ivivid.sh — Complete fix for iVivid repo
# Run: bash fix-ivivid.sh
set -e

cd /media/backup/IMPORTANT/PROJECTS/iVivid

echo "=== [1/7] Ensure .gitignore has .gh-project.json ==="
grep -q ".gh-project.json" .gitignore 2>/dev/null || echo ".gh-project.json" >> .gitignore
echo "  OK"

echo "=== [2/7] Remove nested ivivid/ folder if exists ==="
if [ -d "ivivid" ]; then
    rm -rf ivivid/
    echo "  Removed"
else
    echo "  (not present, skipping)"
fi

echo "=== [3/7] Write proper PROJECT.txt ==="
cat > PROJECT.txt << 'EOF'
name: ivivid
description: Supercharge video on Linux iGPUs - HDR-like color, sharp upscale, punchy audio. One click, no GPU required.
license: MIT
visibility: public
author: sudipdasin
language: Python
version: 1.0.0
keywords: mpv,smplayer,igpu,intel,video,enhancement,hdr,shaders,xfce,linux,configurator,upscaling,audio,480p,1080p
scaffold:
  readme: yes
  license: yes
  contributing: yes
  changelog: yes
  gitignore: yes
  gitattributes: yes
  editorconfig: yes
  notes: yes
  issue_template: yes
  pr_template: yes
  cicd: yes
EOF
echo "  OK"

echo "=== [4/7] Write proper README.md ==="
cat > README.md << 'EOF'
# iVivid

**Make every frame pop on your Linux laptop. No dedicated GPU needed.**

Supercharge video playback on integrated graphics. One click applies HDR-like color, sharp upscaling, and punchy audio — auto-tuned for your specific iGPU.

## Why

Your laptop's integrated GPU can make movies look dramatically better — but finding the right mpv settings, shaders, and audio filters means hours of tinkering. iVivid does it all in one click.

## Install

    sudo apt install python3-tk mpv smplayer

## Run

    python3 ivivid.py

## How it works

1. Open the GUI
2. Select a quality preset: **LIGHT** / **BALANCED** / **MAX**
3. Tweak individual options (hover any checkbox for detailed help)
4. Click **APPLY**
5. Play: `mpv /path/to/video.mp4`

Works with both **mpv** and **SMPlayer** (mpv engine).

## Features

### Video

- 480p to 1080p fullscreen, no black bars, no crop
- Pseudo-HDR look (S-curve contrast, gamma lift, 1.35x saturation, warm tint, soft-clip)
- Adaptive sharpening (edge-aware, no halos or ringing)
- Chroma upscaling (KrigBilateral or CfL_Prediction)
- Debanding (built-in + hdeband GPU shader)
- Temporal dithering
- EWA Lanczos Sharp scaler + sigmoid upscaling
- Hardware decode (VA-API)
- Auto-play next video in folder

### Audio

- Bass boost (0-20dB slider)
- Treble boost (0-20dB slider)
- 3D Surround (stereowiden: narrow / wide / ultra)
- Dynamic compressor
- Loudness normalize (EBU R128)
- Volume up to 150%

### System

- iGPU auto-detection (Intel HD 620, UHD 630, Iris Xe, AMD Radeon)
- Quality presets auto-tuned per iGPU tier
- XFCE compositor auto-disable (biggest performance win)
- Dark theme, tooltips, zero pip dependencies

## Quality Presets

| Preset | Shaders | Best for |
|--------|---------|----------|
| **LIGHT** | soft_look + adaptive-sharpen | HD 620, UHD 630 (guaranteed 60fps) |
| **BALANCED** | vivid_hdr + CfL + adaptive-sharpen | HD 620, UHD 630, Iris Plus |
| **MAX** | vivid_hdr + KrigBilateral + hdeband + adaptive-sharpen | Iris Xe, AMD iGPU 700M+ |

## Hotkeys (during playback)

| Key | Action |
|-----|--------|
| F | Toggle fullscreen |
| CTRL+1 | Shaders ON |
| CTRL+2 | Shaders OFF |
| + / - | Volume +/-5 |

## Requirements

- Python 3.8+
- mpv 0.39+
- python3-tk
- Linux (XFCE preferred, GNOME/KDE work)
- Intel or AMD iGPU with VA-API support
- No pip packages (stdlib only)

## Project Structure

    ivivid/
    ├── ivivid.py                # Main application (single file)
    ├── PROJECT.txt              # Project metadata
    ├── README.md
    ├── LICENSE
    ├── CONTRIBUTING.md
    ├── CHANGELOG.md
    ├── .gitignore
    ├── .gitattributes
    ├── .editorconfig
    ├── NOTES.md
    └── .github/
        ├── ISSUE_TEMPLATE/
        ├── PULL_REQUEST_TEMPLATE.md
        └── workflows/
            └── ci.yml

## License

MIT - see [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Acknowledgments

- mpv and its shader ecosystem
- KrigBilateral, CfL_Prediction, adaptive-sharpen (boned101)
- ravu, hdeband (akirasuper)
- Python stdlib (tkinter, subprocess, json)

---

**One file. One click. Better movies.**
EOF
echo "  OK"

echo "=== [5/7] Update CONTRIBUTING.md ==="
cat > CONTRIBUTING.md << 'EOF'
# Contributing to iVivid

Thanks for considering contributing!

## How to Contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'feat: add new shader option'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

## Commit Messages

Use Conventional Commits:

- `feat:` new feature (new shaders, presets, options)
- `fix:` bug fix
- `docs:` documentation only
- `style:` formatting, no logic change
- `refactor:` code change, no behavior change
- `perf:` performance improvement
- `test:` adding or updating tests
- `chore:` build process, dependencies

## PR Requirements

- Self-reviewed code
- Tested on at least one iGPU
- No new pip dependencies (stdlib only)
- No triple-quoted f-strings with backticks (paste-safe)
- Documentation updated if user-facing change

## Code Style

- Python 3.8+
- Max line length: 120
- No external dependencies
- Tkinter for GUI (stdlib)

## Bug Reports

Include:
- iGPU model (`lspci | grep VGA`)
- mpv version (`mpv --version`)
- Python version
- Steps to reproduce
- Terminal output / traceback
EOF
echo "  OK"

echo "=== [6/7] Commit ==="
git add -A
git commit -m "docs: complete README, PROJECT.txt, CONTRIBUTING, gitignore fix" || echo "  (nothing to commit)"
echo "  OK"

echo "=== [7/7] Push ==="
git push
echo "  OK"

echo ""
echo "============================================"
echo "  DONE"
echo "============================================"
echo ""
echo "  GitHub:  https://github.com/sudipdasin/iVivid"
echo ""
echo "  Files updated:"
echo "    README.md        - Full features, presets, usage"
echo "    PROJECT.txt      - Complete metadata"
echo "    CONTRIBUTING.md  - Fork/branch/PR guide"
echo "    .gitignore       - .gh-project.json excluded"
echo ""
echo "  Remember to rotate your token:"
echo "    github.com/settings/tokens -> revoke old -> new login in app"   
