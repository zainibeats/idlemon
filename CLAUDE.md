# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IdleMon is a PySide6-based Pokemon shiny hunting simulator that displays animated Pokemon encounters with a 1/2000 chance of finding shinies. The application supports two modes: a normal windowed mode with full UI, and a borderless transparent "desktop pet" mode.

## Development Commands

### Running the Application
```bash
# Development mode
python src/main.py

# Or from project root
python -m src.main
```

### Building the Executable
```bash
# Build using PyInstaller (requires main.spec file)
pyinstaller main.spec

# Output will be in dist/IdleMon/
```

### Installing Dependencies
```bash
pip install -r requirements.txt

# Or with specific Python version
python -m pip install -r requirements.txt
```

## Architecture Overview

### Modular Component System
The application follows a clean separation of concerns with distinct manager classes:

1. **main.py (IdleMonWindow)**: Main window class that orchestrates all components and handles window modes (normal vs borderless)
2. **game_controller.py**: Core game logic including encounter system, shiny detection, timer management, and state tracking
3. **ui_manager.py**: All Qt UI components and layouts. Handles both normal mode (with stats panel) and borderless mode (Pokemon only)
4. **data_manager.py**: Pokemon data loading from generation files, shiny count persistence, and data validation via SHA-256 hashes
5. **audio_manager.py**: Sound effect playback using QSoundEffect
6. **config_loader.py**: Configuration management with DEFAULT_CONFIG merged with user config.json
7. **logger.py**: Error logging and shiny encounter history tracking

### Signal-Based Communication
The application uses Qt signals for thread-safe communication between the game controller (which runs encounters in background threads) and the UI:
- `update_encounter`: Triggers when a new Pokemon is encountered
- `update_counter`: Updates the encounter counter
- `update_timer`: Updates elapsed time display
- `shiny_found`: Triggers shiny encounter handling

Connection pattern in main.py:
```python
self.game.signals.update_encounter.connect(self.on_encounter_update)
self.game.signals.shiny_found.connect(self.on_shiny_found)
```

### Threading Model
- **Main thread**: Runs Qt event loop and UI updates
- **Timer thread**: Updates elapsed time every second (game_controller.py:91)
- **Encounter thread**: Runs the Pokemon encounter loop (game_controller.py:107)

All UI updates from background threads must use signals to ensure thread safety.

### Dual Mode System
The application supports two distinct modes controlled by `config["borderless_mode"]`:

**Normal Mode**: Traditional window with background image, stats panel (encounters, timer, shiny count), and continue button

**Borderless Mode**: Frameless transparent window (Qt.FramelessWindowHint + Qt.WA_TranslucentBackground) showing only the Pokemon GIF. Features:
- Draggable via mousePressEvent/mouseMoveEvent
- System tray icon with exit option
- Right-click context menu on Pokemon for continue/exit
- No visible stats or buttons

UI components conditionally render based on `self.borderless_mode` throughout ui_manager.py.

### Configuration System
Configuration loads from `config.json` in the executable directory, merged with DEFAULT_CONFIG in config_loader.py. Key settings:
- `encounter_delay`: Time between encounters (default 0.5s)
- `shiny_rate`: 1 in X chance (default 20 for testing, 2000 in production)
- `rarity_weights`: Spawn rates for "Very Common", "Common", "Semi-rare", "Rare", "Very Rare"
- `borderless_mode`: Enable desktop pet mode
- `mute_audio`: Disable sound effects
- `background_image`: Path (absolute or relative to executable)

Paths are converted to absolute during config loading to support both development and PyInstaller modes.

### Asset Organization
```
assets/
├── gifs/gen1-5/normal/     # Normal Pokemon sprites
├── gifs/gen1-5/shiny/      # Shiny variants
├── sounds/                  # WAV sound effects
├── data/                    # gen1-5_pokemon_names.txt (name,rarity format)
└── images/                  # Background images
```

Pokemon data files are validated using SHA-256 hashes stored in `POKEMON_DATA_HASHES` (config_loader.py:27).

### Data Persistence
- **Shiny count**: Stored in `logs/shiny_count.bin` as base64-encoded integer
- **Shiny history**: Stored in `logs/shinies_encountered.txt` with format: `name | rarity | count`
- **Error logs**: Written to `logs/error.log`

The shiny count file uses base64 encoding and includes corruption detection with automatic reset to 0.

### Path Resolution
The application uses `get_base_path()` to work in both development and PyInstaller modes:
- Development: Returns project root (parent of src/)
- PyInstaller: Returns directory containing the executable

All asset paths are resolved relative to this base path.

## Key Implementation Details

### Shiny Encounter Flow
1. Background thread in `game_controller._encounter_loop()` continuously generates encounters
2. When shiny detected via `check_shiny()`, emits `shiny_found` signal
3. Main window receives signal, plays sound, increments counter, logs encounter
4. UI shows continue button (normal mode) or enables context menu option (borderless)
5. Encounter loop pauses until user continues
6. On continue: resets counter, timer, and restarts encounter loop

### GIF Display System
Pokemon GIFs are located by searching gen1-5 directories for matching names. The `display_pokemon_gif()` method in ui_manager.py uses QMovie for animation with 1.5x scaling.

### Encounter Counter Reset Behavior
The encounter counter resets to 0 after clicking continue from a shiny, but the timer can be reset or continue depending on game state. The `total_shiny_found` counter persists across sessions.

## Important Notes

- The shiny rate in config is currently set to 20 for testing (should be 2000 for production)
- All Pokemon data files must pass SHA-256 validation or the application exits
- Borderless mode requires system tray support (may not work on all Linux environments)
- The application is designed to be portable - all data is stored relative to the executable
