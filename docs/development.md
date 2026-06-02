# Development Guide

This guide covers local development for IdleMon `0.3.0`.

## Requirements

- Python 3.9 or later
- A virtual environment is recommended

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run From Source

Run from the repository root:

```bash
python src/main.py
```

## Project Layout

- `src/main.py`: application entrypoint and top-level wiring
- `src/config_loader.py`: config loading, path resolution, and startup directory creation
- `src/game_controller.py`: encounter loop, timer loop, and shiny logic
- `src/ui_manager.py`: main window UI and borderless mode behavior
- `src/settings_dialog.py`: settings dialog and config persistence
- `src/collection_window.py`: shiny collection UI
- `src/data_manager.py`: shiny count persistence and Pokemon data loading
- `src/logger.py`: error logging and shiny encounter history
- `main.spec`: Windows portable one-folder PyInstaller build
- `assets/`: bundled images, sounds, gifs, and Pokemon data

## Configuration Notes

- `config/config.json` stores only user-facing settings.
- Runtime save data and logs are written under `config/` to preserve the portable Windows layout.
- Asset paths are resolved from the project root in source mode and from the executable folder in packaged mode.

## Linux

Use [linux-setup.md](linux-setup.md) for source-run instructions and Linux troubleshooting.
