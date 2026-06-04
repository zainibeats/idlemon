# IdleMon Project State And Stability Findings

Review date: 2026-06-04

Scope: repository structure, docs, source code, tests, packaging spec, config behavior, and bundled assets. This is a product and architecture review, not a code-change pass.

## Project Goal

IdleMon is a small PySide6 desktop app for idle Pokemon encounter simulation and shiny hunting. The intended production shape is:

- Portable one-folder Windows release.
- Linux source-run only.
- Local writable settings, save data, and logs under `config/`.
- Animated normal and shiny encounter GIFs for generations 1-5.
- A normal windowed mode and an important borderless desktop pet mode.

The project is intentionally simple: a Qt GUI, a game controller driven by Qt timers, a data manager for save and Pokemon data, and small managers for UI, audio, paths, config, logging, settings, and collection display.

## Current State

The current implementation is materially more stable than an early prototype. It already has several good production decisions in place:

- `GameController` uses `QTimer`, keeping the encounter loop on the Qt event loop instead of spinning background threads.
- Config is validated before runtime use.
- Mutable runtime paths are centralized through `src/paths.py`.
- Save data writes are atomic via temp file plus `os.replace`.
- Pokemon name data is cached after first load.
- Logging is file-backed and idempotent for the same log path.
- Persisted user config is limited to user-facing settings.
- Tests cover config loading, save persistence, data parsing, logger setup, and GIF asset coverage.

Validation performed:

- `python -m pytest`: 15 passed.
- `python -m compileall -q src`: passed.
- Bundled GIF count: 1,298.
- Bundled asset size: about 129 MB.
- Largest GIF file: about 1.3 MB.

One local note: `config/config.json` is currently modified from `borderless_mode: false` to `true`. I treated this as an existing user change and did not modify it.

## Main Stability And Resource Risks

### 1. Main encounter GIF loading is the biggest hot path

References: `src/ui_manager.py:215`, `src/ui_manager.py:223`, `src/utils.py:19`

Every encounter searches up to five generation directories, creates a new `QMovie`, scales it, assigns it to the label, and starts it. At the default 2.5-second encounter delay this is probably acceptable, but it is the most likely source of gradual memory churn, disk churn, or UI hiccups during long sessions.

Recommended direction:

- Build a Pokemon asset index once at startup from the loaded Pokemon data.
- Store the resolved normal and shiny GIF path with each Pokemon entry.
- Cache only the currently displayed movie and possibly a small bounded LRU cache of recent movies.
- Explicitly stop the previous movie before replacing it.

Avoid preloading all 1,298 GIFs into memory. The asset folder is too large for that to be a good default.

### 2. Collection window can create many `QMovie` objects at once

References: `src/collection_window.py:68`, `src/collection_window.py:326`

The collection window creates one widget and one `QMovie` per visible collection item. Animation starts only on hover, which is good, but the movie objects still exist. If a user eventually collects hundreds of unique shinies, opening or resizing the collection can create many GIF objects and recreate them repeatedly.

Recommended direction:

- Keep hover-only animation.
- Add a practical cap through pagination or virtualized/lazy rendering if the collection can grow large.
- Avoid rebuilding every item on every resize; recalculate columns only when the column count changes.

This can remain simple until real collection sizes make it a problem.

### 3. Encounter weighting can silently exclude Pokemon

Reference: `src/game_controller.py:134`

Weights are built from rarity strings in data files. Unknown rarity values receive weight `0`, so those Pokemon remain in memory but are never encountered. Config validation ensures the configured weights are sane, but not that every data-file rarity maps to a positive weight.

Recommended direction:

- Validate loaded Pokemon rarity values against configured rarity weights.
- Log or block startup if any data entries use unknown rarity labels.

This prevents silent content bugs.

### 4. Save-data corruption recovery is stable but destructive

Reference: `src/data_manager.py`

Invalid save data is logged and replaced with defaults. That keeps the app running, but it discards user progress.

Recommended direction:

- Before resetting corrupted save data, rename the bad file to a timestamped backup.
- Keep the current default reset behavior after backup.

This preserves stability while giving users a recovery path.

### 5. Packaging includes mutable default config

Reference: `main.spec`

The PyInstaller spec includes `config/` in the bundled output. This supports portable defaults, but it also means packaged builds may ship with whatever local config is present unless release packaging is careful.

Recommended direction:

- Ensure release builds start from a clean, intentional `config/config.json`.
- Consider generating the release config during packaging instead of bundling the working tree's mutable config directory.

This matters because the current local config has `borderless_mode` changed to `true`.

## Ground-Up Architecture I Would Use

If building this from scratch, I would keep the same broad shape but tighten ownership around assets and runtime state:

- `AppPaths`: one small path object for app root, asset root, config file, save file, and log dir.
- `UserSettings`: only persisted settings: borderless mode, mute audio, background image.
- `GameRules`: internal constants: encounter delay, shiny rate, rarity weights, enabled generations.
- `PokemonCatalog`: loads data files once, validates rarity labels, and resolves GIF paths once.
- `SaveStore`: atomic JSON save/load with corrupt-file backup.
- `EncounterEngine`: pure encounter state and random selection, driven externally by a Qt timer.
- `MainWindow`: wires Qt signals, UI updates, audio, settings, collection window, and lifecycle.
- `GifDisplay`: owns current `QMovie`, stops replacement movies explicitly, and optionally uses a small bounded cache.

The important principle is to keep runtime data small and bounded. Load Pokemon metadata once, resolve paths once, load media on demand, and avoid unbounded caches.

## Simplicity Versus Stability

The current app should not grow a large framework or complicated service layer. The simplest stable path is:

1. Keep Qt timers and the current single-process model.
2. Do not add background workers unless a measured UI stall requires them.
3. Do not preload GIF assets.
4. Add a small Pokemon catalog/index to remove repeated file probing.
5. Add explicit current-movie cleanup in the main display.
6. Add save backup before corruption reset.
7. Keep tests focused around config, save recovery, catalog validation, and encounter selection.

## Questions To Align On Product Direction

1. Should users ever be able to change `shiny_rate`, `encounter_delay`, rarity weights, or enabled generations, or should those remain developer-only constants?
2. Is the collection expected to scale to hundreds of unique shinies per user, or is a simple grid acceptable for the foreseeable future?
3. Should borderless mode start at app launch only, or should switching it live without restart become a product goal?
4. Should release builds always start in normal windowed mode, regardless of the local developer config?
5. Is preserving corrupted save files important enough to add backup files under `config/`, even though it slightly increases file-management complexity?

## Recommended Next Steps

Priority order:

1. Add a `PokemonCatalog` or equivalent lightweight index for Pokemon metadata and GIF paths.
2. Stop and replace the active main `QMovie` explicitly in `UIManager`.
3. Validate data-file rarity values against configured rarity weights.
4. Back up corrupted save data before resetting it.
5. Make release packaging use a known clean config.
6. Revisit collection pagination or virtualization only if real user collections become large.

Overall, the project is in a good maintainable state for a small desktop app. The main blind spot is not CPU from the encounter loop; it is repeated animated media allocation and future collection-window scaling.
