# Dev Environment & Run Setup

## What it is

How the project's dependencies, run script, and editor integration fit together — the "getting it running" concept, as opposed to the image-processing pipeline itself.

## Key files / paths

- `pyproject.toml` — PEP 621 dependency manifest (`opencv-python`, `numpy`), no `[build-system]` since the app runs as scripts
- `run.sh` — cross-platform setup + run script
- `.vscode/launch.json` — F5 debug config (runs `src/main.py` with cwd `src/`)
- `.vscode/tasks.json` — `Install Python Dependencies`, `Clean Python Project`, `Format with Black` tasks
- `.vscode/settings.json` — Black as formatter, format-on-save

## How it works

- `run.sh` is the primary entry point: finds a Python 3.11+ interpreter (`python3` then `python`) — 3.11+ is required only so it can read `pyproject.toml`'s dependency list with the standard-library `tomllib` module — checks whether everything declared in `[project.dependencies]` is installed and installs whatever's missing, then runs `src/main.py` from the `src/` directory.
- Every step is logged to both the console and `Logs/run_<timestamp>.log`, including per-package install status (version + location) and a final summary (image/result counts, timing).
- The VS Code debug config (`launch.json`) takes a different path: its `preLaunchTask` (`Install Python Dependencies`) reads the same `pyproject.toml` dependency list via an inline `tomllib` one-liner and installs into the active `.venv`, rather than reusing `run.sh`.
- `launch.json` also declares `"envFile": "${workspaceFolder}/.env"` — no `.env` file exists in the repo and no source file reads `os.environ`, so this is currently a no-op hook, not an active config path.

## Gotchas / conventions

- Dependency-checking logic exists in two independent places (`run.sh` and the VS Code task) — both parse `pyproject.toml` directly rather than one calling the other. Keep both in sync if the dependency-install logic changes.
- `run.sh` requires Bash; on Windows it needs WSL or Git Bash. The VS Code launch config is the native alternative on plain Windows.
- No test suite or `tests/` directory exists yet — see [[known_gaps]].
