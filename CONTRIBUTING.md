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
