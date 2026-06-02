"""Configuration management module"""
import json
import sys
from pathlib import Path


def get_base_path():
    """Get application base path for both dev and PyInstaller modes"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent


PROJECT_ROOT = get_base_path()

DEFAULT_CONFIG = {
    "encounter_delay": 2.5,
    "rarity_weights": {
        "Very Common": 45,
        "Common": 30,
        "Semi-rare": 17,
        "Rare": 7,
        "Very Rare": 1
    },
    "shiny_rate": 2000,
    "mute_audio": False,
    "borderless_mode": False,
    "save_data_file": "data/save_data.json",
    "background_image": "assets/images/default_background.jpg",
    "pokemon_data_files": {
        "gen1": "assets/data/gen1_pokemon_names.txt",
        "gen2": "assets/data/gen2_pokemon_names.txt",
        "gen3": "assets/data/gen3_pokemon_names.txt",
        "gen4": "assets/data/gen4_pokemon_names.txt",
        "gen5": "assets/data/gen5_pokemon_names.txt"
    }
}


def _normalize_path_value(value):
    """Normalize config path strings so Windows-style paths still parse on Linux."""
    if isinstance(value, str):
        return value.replace("\\", "/")
    return value


def _create_directories():
    """Create required directory structure"""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
    (PROJECT_ROOT / "data").mkdir(exist_ok=True)
    (PROJECT_ROOT / "assets" / "data").mkdir(parents=True, exist_ok=True)
    for gen in range(1, 6):
        (PROJECT_ROOT / "assets" / "gifs" / f"gen{gen}" / "normal").mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "assets" / "gifs" / f"gen{gen}" / "shiny").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "assets" / "images").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "assets" / "sounds").mkdir(parents=True, exist_ok=True)


def load_config():
    """Load configuration from file, merge with defaults, and validate required data files."""
    _create_directories()

    # Load user config if exists
    config_file = PROJECT_ROOT / "config.json"
    user_config = {}
    if config_file.exists():
        try:
            user_config = json.loads(config_file.read_text())
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading config file: {e}. Using default settings.")

    # Merge user config with defaults
    config = {**DEFAULT_CONFIG, **user_config}

    config["background_image"] = _normalize_path_value(config["background_image"])
    config["save_data_file"] = _normalize_path_value(config["save_data_file"])
    config["pokemon_data_files"] = {
        gen: _normalize_path_value(path)
        for gen, path in config["pokemon_data_files"].items()
    }

    # Convert relative paths to absolute
    path = Path(config["save_data_file"])
    if not path.is_absolute():
        config["save_data_file"] = str(PROJECT_ROOT / path)

    # Convert Pokemon data paths to absolute
    first_path = Path(next(iter(config["pokemon_data_files"].values())))
    if not first_path.is_absolute():
        config["pokemon_data_files"] = {
            gen: str(PROJECT_ROOT / path)
            for gen, path in config["pokemon_data_files"].items()
        }

    missing_files = [
        file_path for file_path in config["pokemon_data_files"].values()
        if not Path(file_path).exists()
    ]
    if missing_files:
        print("Error: required Pokemon data files are missing:")
        for file_path in missing_files:
            print(f" - {file_path}")
        sys.exit(1)

    return config
