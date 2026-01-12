"""Configuration management module"""
import json
import os
import sys
from pathlib import Path

# Average time per shiny is ENCOUNTER_DELAY * SHINY_RATE = X seconds - Default is ~1.39 hours
ENCOUNTER_DELAY = 2.5 # Time between encounters (seconds) - Default is 2.5
SHINY_RATE = 2000 # 1 in X chance of shiny - Default is 2000

def get_base_path():
    """
    Get application base path for both dev and PyInstaller modes

    Returns:
        Path: Base path for the application
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller mode: use executable directory
        return Path(sys.executable).parent
    else:
        # Development mode: use project root
        return Path(__file__).parent.parent


# Set application root path
PROJECT_ROOT = get_base_path()

# SHA-256 hashes for data file verification
POKEMON_DATA_HASHES = {
    "gen1": "bb1fd5dbb801d1e8f453d39eedc85f20fb96c804613041b236581e4037645b5f",
    "gen2": "6bac78b82268154f307cbdff766e2d71c67f48881bd296f5f1d1ac6af556b5c3",
    "gen3": "edc5d92ae40dd6d8cc7205537d58b570fede40970ba2cfd8bb9e7ab3241d21cb",
    "gen4": "56e5512eff1684bf4fac1d512d5ab8fd9fe49c1058260f85e3a43a57fbd8b8eb",
    "gen5": "35f7fbd7e12604d46517389f8d1133f06e67d93b3dbe4fc6b894f26b658c0f73"
}


def validate_pokemon_data_file(gen, file_path):
    """
    Verify Pokemon data file integrity using SHA-256 hash

    Args:
        gen: Generation identifier (e.g., "gen1", "gen2")
        file_path: Path to the data file

    Returns:
        bool: True if validation passes, False otherwise
    """
    import hashlib

    if not os.path.exists(file_path):
        return False

    with open(file_path, "rb") as file:
        file_hash = hashlib.sha256(file.read()).hexdigest()

    return file_hash == POKEMON_DATA_HASHES.get(gen, "")

# Default configuration settings
DEFAULT_CONFIG = {
    # Gameplay settings
    "encounter_delay": ENCOUNTER_DELAY,
    "rarity_weights": {          # Spawn rate weights
        "Very Common": 45,
        "Common": 30,
        "Semi-rare": 17,
        "Rare": 7,
        "Very Rare": 1
    },
    "shiny_rate": SHINY_RATE,
    "mute_audio": False,        # Audio mute state
    "borderless_mode": False,   # Borderless transparent window mode

    # File paths
    "shiny_count_file": "logs/shiny_count.bin",
    "shinies_encounter_file": "logs/shinies_encountered.txt",
    "background_image": "assets/images/default_background.jpg",

    # Pokemon data files
    "pokemon_data_files": {
        "gen1": "assets/data/gen1_pokemon_names.txt",
        "gen2": "assets/data/gen2_pokemon_names.txt",
        "gen3": "assets/data/gen3_pokemon_names.txt",
        "gen4": "assets/data/gen4_pokemon_names.txt",
        "gen5": "assets/data/gen5_pokemon_names.txt"
    }
}

class ConfigManager:
    """Manages application configuration and directory structure"""

    def __init__(self, config_file="config.json"):
        self.config_file = str(PROJECT_ROOT / config_file)
        self._create_directories()
        self.config = self.load_config()

    def _create_directories(self):
        """Create required directory structure"""
        (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
        (PROJECT_ROOT / "assets/data").mkdir(parents=True, exist_ok=True)
        for gen in range(1, 6):
            (PROJECT_ROOT / f"assets/gifs/gen{gen}/normal").mkdir(parents=True, exist_ok=True)
            (PROJECT_ROOT / f"assets/gifs/gen{gen}/shiny").mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "assets/images").mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "assets/sounds").mkdir(parents=True, exist_ok=True)

    def validate_pokemon_data(self, gen, file_path):
        """Verify Pokemon data file integrity using SHA-256 hash"""
        if not validate_pokemon_data_file(gen, file_path):
            print(f"Error: {file_path} validation failed. Please ensure the file exists and has not been modified.")
            sys.exit(1)
            
    def load_config(self):
        """Load configuration from file or use defaults"""
        # Load user config if exists
        user_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    user_config = json.load(file)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading config file: {e}. Using default settings.")

        # Merge user config with defaults
        config = {**DEFAULT_CONFIG, **user_config}

        # Convert paths to absolute
        path_keys = ["shiny_count_file", "shinies_encounter_file"]
        for key in path_keys:
            if not os.path.isabs(config[key]):
                config[key] = str(PROJECT_ROOT / config[key])

        # Convert Pokemon data paths to absolute
        if not os.path.isabs(next(iter(config["pokemon_data_files"].values()))):
            config["pokemon_data_files"] = {
                gen: str(PROJECT_ROOT / path)
                for gen, path in config["pokemon_data_files"].items()
            }

        # Verify all Pokemon data files
        for gen, file_path in config["pokemon_data_files"].items():
            self.validate_pokemon_data(gen, file_path)

        return config

# Helper functions
def load_config():
    """Create config manager and return config"""
    config_manager = ConfigManager()
    return config_manager.config

def check_file_exists(file_path):
    """Check if file exists and warn if missing"""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} does not exist.")
        return False
    return True
