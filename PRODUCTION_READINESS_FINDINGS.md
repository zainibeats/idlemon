# Production Readiness Findings

Review date: 2026-06-02

Scope: follow-up static review of the Python/PySide6 desktop app, docs, config, packaging spec, and bundled assets after the first cleanup pass.

## Quick Verdict

IdleMon is closer to production-ready after the first fixes. The timer lifecycle now uses Qt-native timers, save data is stored as atomic JSON, generated runtime files are ignored, and focused tests cover config loading, save round trips, data parsing, and asset coverage.

The remaining production risks are mostly around config validation, user data location, path ownership, and production diagnostics.

## Must Fix Before Production

### 1. Stop writing user save data and mutable config into the app install directory by default

References: `src/config_loader.py:7`, `src/config_loader.py:15`, `src/config_loader.py:46`, `src/main.py:135`, `src/main.py:176`, `main.spec:13`

The app still resolves `PROJECT_ROOT` to the source root or executable folder, then stores `config.json`, `data/save_data.json`, and `logs/` there. That works for a portable one-folder build, but it is not a general production convention. It also means packaged users may write progress into the extracted program folder.

Recommended direction depends on product vision:

- If the Windows build is intentionally portable, document that as a product constraint and keep user data beside the executable.
- If production should behave like a normal desktop app, store mutable data in the user data/config directory, using a standard helper such as `platformdirs`.

Question: should IdleMon remain intentionally portable-first, or should it use OS user data directories for production?

### 2. Validate config values before runtime use

References: `src/config_loader.py:60`, `src/game_controller.py:35`, `src/game_controller.py:47`, `src/game_controller.py:80`, `src/game_controller.py:139`

`load_config()` merges user JSON into defaults, but does not validate the core runtime settings. Invalid values can still break runtime behavior:

- `shiny_rate <= 0` can crash `random.randint`.
- `encounter_delay` can be negative or non-numeric.
- `rarity_weights` can contain all zero/invalid values, which breaks `random.choices`.
- `pokemon_data_files` can be partly absolute and partly relative, but only the first path is checked to decide conversion.

Recommended direction: keep validation small and explicit. Clamp or reject the few user-facing fields, and treat internal asset paths as constants unless there is a clear reason users need to configure them.

## Simplification And Refactor Opportunities

### 1. Centralize path ownership

References: `src/config_loader.py:7`, `src/main.py:51`, `src/data_manager.py:12`, `src/settings_dialog.py:17`, `src/utils.py:5`

Path resolution is spread across config loading, main window setup, data manager, settings dialog, and utility functions. A small `paths.py` or `AppPaths` object would simplify this:

- app/assets root
- user config path
- user save/log directory
- asset lookup helpers

This would remove repeated `PROJECT_ROOT` passing and reduce packaged/source path edge cases.

### 2. Separate config defaults from user settings

References: `src/config_loader.py:17`, `src/settings_dialog.py:215`, `src/settings_dialog.py:230`

`config.json` only exposes three user-facing settings, but the in-code default config includes game constants and asset paths. The settings dialog saves the fully merged config back to disk, including internal defaults. That makes future default changes harder because old user configs can freeze old internal values.

Recommended direction: keep user settings separate from internal constants. Persist only actual user preferences unless advanced config is intentionally part of the product.

Question: should `encounter_delay`, `shiny_rate`, rarity weights, and generation data paths be user-editable, or are they internal constants?

### 3. Simplify UI styling duplication

References: `src/ui_manager.py:104`, `src/ui_manager.py:176`, `src/ui_manager.py:274`, `src/settings_dialog.py:58`, `src/collection_window.py:1`

Stylesheets are repeated across modules and sometimes repeated within a single method. `UIColors` helps, but the app would be simpler with a few shared style constants or helper functions for common buttons, labels, panels, and inputs.

Recommended direction: do not introduce a large design system. Just extract the repeated button/label/panel styles that are already duplicated.

### 4. Replace console prints with configured logging or user-visible errors

References: `src/config_loader.py:71`, `src/data_manager.py:59`, `src/game_controller.py:86`, `src/game_controller.py:116`, `src/game_controller.py:164`, `src/game_controller.py:166`

The app runs packaged with `console=False`, so many `print()` diagnostics are invisible to users. Production behavior should be either:

- log to `error.log` or an application log, or
- show a small `QMessageBox` for startup-blocking problems.

The "shiny nearby" console Easter egg is invisible in packaged builds and can probably be removed unless it becomes an in-app feature.

### 5. Make logger setup idempotent

References: `src/logger.py:13`, `src/logger.py:18`

`LogManager` adds a new `FileHandler` every time it is constructed for the same logger name. The current app appears to construct it once, but tests or future windows can accidentally duplicate log lines.

Recommended direction: either use a per-instance logger name or check whether the file handler already exists before adding one.

### 6. Consider whether `requirements.txt` should separate runtime and development dependencies

Reference: `requirements.txt`

`pyinstaller` and `pytest` are build/test dependencies but are installed for source users. For simplicity this is acceptable, but production polish usually separates runtime and build tooling:

- `requirements.txt` for runtime
- `requirements-dev.txt` for build/test tools

This is optional, but it aligns with common Python packaging conventions.

## Validation Notes

- `python -m compileall -q src` passed during the original review.
- All 649 Pokemon data entries have matching normal and shiny GIF files.
- Default configured background exists at `assets/images/default_background.jpg`.
- Packaging spec includes `assets`, `config.json`, `README.md`, and `LICENSE`.
- Focused pytest tests now cover config loading, save persistence, Pokemon data parsing, and GIF asset coverage.

## Open Questions

1. Should production builds be portable-first, with save data beside the executable, or OS-native, with save data in the user's app data directory?
2. Are shiny rate, encounter delay, rarity weights, and enabled generations part of the intended user-facing configuration?
3. Is borderless mode the primary production experience, or is the normal window equally important?
4. Do you want Linux to remain source-only, or should production readiness include Linux packaging later?

## Suggested Iteration Order

1. Decide portable vs OS-native data location.
2. Consolidate paths and config validation.
3. Separate persisted user settings from internal defaults.
4. Replace console-only diagnostics with logging or user-visible errors.
5. Make logger setup idempotent.
6. Deduplicate the most repeated UI styles.
7. Split runtime and development requirements if packaging polish is in scope.
