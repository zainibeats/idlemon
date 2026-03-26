"""Configuration management module"""
import hashlib
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

# SHA-256 hashes for data file verification
POKEMON_DATA_HASHES = {
    "gen1": "bb1fd5dbb801d1e8f453d39eedc85f20fb96c804613041b236581e4037645b5f",
    "gen2": "6bac78b82268154f307cbdff766e2d71c67f48881bd296f5f1d1ac6af556b5c3",
    "gen3": "edc5d92ae40dd6d8cc7205537d58b570fede40970ba2cfd8bb9e7ab3241d21cb",
    "gen4": "56e5512eff1684bf4fac1d512d5ab8fd9fe49c1058260f85e3a43a57fbd8b8eb",
    "gen5": "35f7fbd7e12604d46517389f8d1133f06e67d93b3dbe4fc6b894f26b658c0f73"
}

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
    "shiny_count_file": "logs/shiny_count.bin",
    "shinies_encounter_file": "logs/shinies_encountered.txt",
    "background_image": "assets/images/default_background.jpg",
    "pokemon_data_files": {
        "gen1": "assets/data/gen1_pokemon_names.txt",
        "gen2": "assets/data/gen2_pokemon_names.txt",
        "gen3": "assets/data/gen3_pokemon_names.txt",
        "gen4": "assets/data/gen4_pokemon_names.txt",
        "gen5": "assets/data/gen5_pokemon_names.txt"
    }
}


def validate_pokemon_data_file(gen, file_path):
    """Verify Pokemon data file integrity using SHA-256 hash"""
    file_path = Path(file_path)
    if not file_path.exists():
        return False
    file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return file_hash == POKEMON_DATA_HASHES.get(gen, "")


def _create_directories():
    """Create required directory structure"""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
    (PROJECT_ROOT / "assets" / "data").mkdir(parents=True, exist_ok=True)
    for gen in range(1, 6):
        (PROJECT_ROOT / "assets" / "gifs" / f"gen{gen}" / "normal").mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "assets" / "gifs" / f"gen{gen}" / "shiny").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "assets" / "images").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "assets" / "sounds").mkdir(parents=True, exist_ok=True)


def load_config():
    """Load configuration from file, merge with defaults, validate data files"""
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

    # Convert relative paths to absolute
    for key in ("shiny_count_file", "shinies_encounter_file"):
        path = Path(config[key])
        if not path.is_absolute():
            config[key] = str(PROJECT_ROOT / path)

    # Convert Pokemon data paths to absolute
    first_path = Path(next(iter(config["pokemon_data_files"].values())))
    if not first_path.is_absolute():
        config["pokemon_data_files"] = {
            gen: str(PROJECT_ROOT / path)
            for gen, path in config["pokemon_data_files"].items()
        }

    # Verify all Pokemon data files
    for gen, file_path in config["pokemon_data_files"].items():
        if not validate_pokemon_data_file(gen, file_path):
            print(f"Error: {file_path} validation failed. Please ensure the file exists and has not been modified.")
            sys.exit(1)

    return config
