# Development Guide

This guide covers development setup, building from source, and technical details for IdleMon.

## Requirements

For building from source:
- Python 3.8 or later
- Required libraries listed in requirements.txt

### Installing Dependencies

```bash
# Using pip (Windows/Linux)
pip install -r requirements.txt

# Or if you have multiple Python versions
python -m pip install -r requirements.txt
```

---

## Running from Source

### Development Mode
```bash
# Run directly from source
python src/main.py

# Or from project root
python -m src.main
```

### Windows Portable Version
1. Download the latest release
2. Extract the zip file anywhere you like
3. Run `IdleMon.exe` from the extracted folder

The application is fully portable:
- Can be run from any location
- All data is stored in the application folder
- No installation required
- No system modifications

---

## Building from Source

### Windows
1. Clone the repository
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Build the executable:
   ```bash
   pyinstaller main.spec
   ```
4. The portable version will be created in `dist/IdleMon`

### Linux
See the [Linux branch](https://github.com/zainibeats/idlemon/tree/linux) for Linux-specific build instructions.

---

## Project Architecture

For detailed technical information about the codebase architecture, see [CLAUDE.md](../CLAUDE.md) which covers:
- Modular component system
- Signal-based communication
- Threading model
- Configuration system
- And more...

---

## Portable Directory Structure
```
IdleMon/
├── IdleMon.exe
├── assets/
│   ├── gifs/
│   │   ├── gen1/
│   │   │   ├── normal/
│   │   │   └── shiny/
│   │   ├── gen2/
│   │   │   ├── normal/
│   │   │   └── shiny/
│   │   ├── gen3/
│   │   │   ├── normal/
│   │   │   └── shiny/
│   │   ├── gen4/
│   │   │   ├── normal/
│   │   │   └── shiny/
│   │   └── gen5/
│   │       ├── normal/
│   │       └── shiny/
│   ├── sounds/
│   │   ├── shiny_sound1.wav
│   │   └── continue_sound1.wav
│   ├── data/
│   │   ├── gen1_pokemon_names.txt
│   │   ├── gen2_pokemon_names.txt
│   │   ├── gen3_pokemon_names.txt
│   │   ├── gen4_pokemon_names.txt
│   │   └── gen5_pokemon_names.txt
│   └── images/
│       └── background.png
├── config.json (can be edited via Settings dialog)
└── logs/      (created automatically)
    ├── shiny_count.bin         (total shiny count)
    ├── shinies_encountered.txt (shiny collection data)
    └── error.log
```
