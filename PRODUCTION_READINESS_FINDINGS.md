# Production Readiness Findings

Review date: 2026-06-02

Scope: static review of the Python/PySide6 desktop app, docs, config, packaging spec, and bundled assets. No source fixes were made.

## Quick Verdict

IdleMon is close to usable as a small desktop pet, but I would not call it production-ready yet. The main blockers are around runtime lifecycle, save/config resilience, and packaging conventions. The app has a simple structure and all Pokemon data entries have matching normal and shiny GIFs, which is a strong base for a cleanup pass.

## Must Fix Before Production

### 1. Replace ad hoc Python threads with Qt-native timers or worker lifecycle management

References: `src/game_controller.py:79`, `src/game_controller.py:96`, `src/game_controller.py:109`, `src/game_controller.py:113`, `src/main.py:119`, `src/main.py:164`

`GameController` starts daemon `threading.Thread` loops for both the timer and encounters. This is more complex than needed for a Qt app and creates lifecycle risks:

- `continue_hunt()` can start a new encounter thread without joining or explicitly stopping the previous one.
- `closeEvent()` only stops the timer flag, not the encounter loop.
- Shared fields such as `total_encounters`, `shiny_found_flag`, `timer_running`, and `start_time` are read/written across threads without synchronization.
- The work is timer-based UI/game state, which is a natural fit for `QTimer` on the Qt event loop.

Recommended direction: use one or two `QTimer` instances owned by the main/window/controller object. This should remove most threading complexity rather than adding locks.

### 2. Stop writing user save data and mutable config into the app install directory by default

References: `src/config_loader.py:7`, `src/config_loader.py:15`, `src/config_loader.py:48`, `src/main.py:132`, `src/main.py:174`, `main.spec:13`

The app currently resolves `PROJECT_ROOT` to the source root or executable folder, then stores `config.json` and `logs/` there. That works for a portable one-folder build, but it is not a general production convention. It also means packaged users may write progress into the extracted program folder.

Recommended direction depends on product vision:

- If the Windows build is intentionally portable, document that as a product constraint and keep user data beside the executable.
- If production should behave like a normal desktop app, store mutable data in the user data/config directory, using a standard helper such as `platformdirs`.

Question: should IdleMon remain intentionally portable-first, or should it use OS user data directories for production?

### 3. Make save writes atomic and use plain structured files

References: `src/data_manager.py:18`, `src/data_manager.py:34`, `src/logger.py:40`, `src/logger.py:48`

`shiny_count.bin` is a base64-encoded integer, and the collection history is a custom pipe-delimited text file. Both files are rewritten directly. A crash or power loss during write can corrupt progress, and base64 adds obscurity without adding useful safety.

Recommended direction: use one JSON save file with a small schema, write to a temporary file, then atomically replace the old file. For a desktop pet, JSON is simpler, inspectable, and conventional.

Question: do you want save data to be human-editable, or intentionally hidden from casual editing?

### 4. Validate config values before runtime use

References: `src/config_loader.py:59`, `src/config_loader.py:72`, `src/game_controller.py:35`, `src/game_controller.py:62`, `src/game_controller.py:121`

`load_config()` merges user JSON into defaults, but does not validate types or ranges. Invalid values can break runtime behavior:

- `shiny_rate <= 0` can crash `random.randint`.
- `encounter_delay` can be negative or non-numeric.
- `rarity_weights` can contain all zero/invalid values, which breaks `random.choices`.
- `pokemon_data_files` can be partly absolute and partly relative, but only the first path is checked to decide conversion.

Recommended direction: keep validation small and explicit. Clamp or reject the few user-facing fields, and treat internal asset paths as constants unless there is a clear reason users need to configure them.

### 5. Add at least a smoke-testable startup path

References: no test files found; syntax check only passed with `python -m compileall -q src`

There is no automated test coverage. Full GUI testing is not required before production for a project this size, but the risky parts can be tested without showing a window:

- config loading and validation
- Pokemon data parsing
- GIF coverage for all data entries
- save load/write round trips
- collection aggregation

Recommended direction: add `pytest` and a small test suite around non-UI logic. Keep GUI tests optional.

## Simplification And Refactor Opportunities

### 1. Centralize path ownership

References: `src/config_loader.py:7`, `src/main.py:51`, `src/data_manager.py:9`, `src/settings_dialog.py:17`, `src/utils.py:5`

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

References: `src/main.py:16`, `src/game_controller.py:72`, `src/game_controller.py:145`, `src/data_manager.py:26`, `src/config_loader.py:69`

The app runs packaged with `console=False`, so many `print()` diagnostics are invisible to users. Production behavior should be either:

- log to `error.log` or an application log, or
- show a small `QMessageBox` for startup-blocking problems.

The "shiny nearby" console Easter egg is invisible in packaged builds and can probably be removed unless it becomes an in-app feature.

### 5. Make logger setup idempotent

References: `src/logger.py:13`, `src/logger.py:18`

`LogManager` adds a new `FileHandler` every time it is constructed for the same logger name. The current app appears to construct it once, but tests or future windows can accidentally duplicate log lines.

Recommended direction: either use a per-instance logger name or check whether the file handler already exists before adding one.

### 6. Keep production artifacts out of the repo

References: `.gitignore:122`, current workspace contains `logs/error.log`, `logs/shinies_encountered.txt`, `logs/shiny_count.bin`, and `src/__pycache__/`

The ignore file ignores the save filenames only at repo root, not under `logs/`. The workspace currently contains generated runtime files. These should not be versioned or reviewed as source.

Recommended direction: ignore `logs/` or at least `logs/*.log`, `logs/shinies_encountered.txt`, and `logs/shiny_count.bin`; remove generated cache/log files from version control if tracked.

### 7. Consider whether `requirements.txt` should separate runtime and build dependencies

Reference: `requirements.txt`

`pyinstaller` is build-only but installed for source users. For simplicity this is acceptable, but production polish usually separates runtime and build tooling:

- `requirements.txt` for runtime
- `requirements-dev.txt` for build/test tools

This is optional, but it aligns with "known-good conventions."

## Validation Notes

- `python -m compileall -q src` passed.
- All 649 Pokemon data entries have matching normal and shiny GIF files.
- Default configured background exists at `assets/images/default_background.jpg`.
- Packaging spec includes `assets`, `config.json`, `README.md`, and `LICENSE`.
- No test, lint, type-check, or CI configuration was found.

## Open Questions

1. Should production builds be portable-first, with save data beside the executable, or OS-native, with save data in the user's app data directory?
2. Should save data be easy for users to inspect/edit, or mildly hidden from casual editing?
3. Are shiny rate, encounter delay, rarity weights, and enabled generations part of the intended user-facing configuration?
4. Is borderless mode the primary production experience, or is the normal window equally important?
5. Do you want Linux to remain source-only, or should production readiness include Linux packaging later?

## Suggested Iteration Order

1. Decide portable vs OS-native data location.
2. Replace thread loops with `QTimer`.
3. Consolidate paths and config validation.
4. Move saves to atomic JSON persistence.
5. Add focused tests for config, data parsing, save round trips, and asset coverage.
6. Clean generated files and tighten `.gitignore`.
7. Deduplicate the most repeated UI styles.
