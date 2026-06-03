"""Configuration management module"""
from copy import deepcopy
import json
import numbers
import sys
from pathlib import Path

import paths
from paths import PROJECT_ROOT, get_config_file, get_logs_dir

DEFAULT_USER_SETTINGS = {
    "mute_audio": False,
    "borderless_mode": False,
    "background_image": "assets/images/default_background.jpg",
}

USER_CONFIG_KEYS = frozenset(DEFAULT_USER_SETTINGS)

DEFAULT_RUNTIME_CONFIG = {
    "encounter_delay": 2.5,
    "rarity_weights": {
        "Very Common": 45,
        "Common": 30,
        "Semi-rare": 17,
        "Rare": 7,
        "Very Rare": 1
    },
    "shiny_rate": 2000,
    "save_data_file": "save_data.json",
    "pokemon_data_files": {
        "gen1": "assets/data/gen1_pokemon_names.txt",
        "gen2": "assets/data/gen2_pokemon_names.txt",
        "gen3": "assets/data/gen3_pokemon_names.txt",
        "gen4": "assets/data/gen4_pokemon_names.txt",
        "gen5": "assets/data/gen5_pokemon_names.txt"
    }
}

DEFAULT_CONFIG = {
    **deepcopy(DEFAULT_RUNTIME_CONFIG),
    **deepcopy(DEFAULT_USER_SETTINGS),
}


def _create_directories():
    """Create writable portable runtime directories."""
    config_dir = paths.get_config_dir()
    config_dir.mkdir(exist_ok=True)
    paths.get_logs_dir().mkdir(exist_ok=True)


def _load_user_config():
    """Load persisted user-facing settings from the portable config file."""
    config_file = paths.get_config_file()
    legacy_config_file = paths.get_legacy_config_file()
    if not config_file.exists() and legacy_config_file.exists():
        config_file = legacy_config_file
    if not config_file.exists():
        return {}

    try:
        loaded_config = json.loads(config_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading config file: {e}. Using default settings.")
        return {}

    if not isinstance(loaded_config, dict):
        print("Error loading config file: root value must be an object. Using default settings.")
        return {}

    return {
        key: value
        for key, value in loaded_config.items()
        if key in USER_CONFIG_KEYS
    }


def _require_path_string(config, key):
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")


def _validate_config(config):
    """Validate runtime configuration before path resolution and game use."""
    encounter_delay = config.get("encounter_delay")
    if (
        isinstance(encounter_delay, bool)
        or not isinstance(encounter_delay, numbers.Real)
        or encounter_delay <= 0
    ):
        raise ValueError("encounter_delay must be a positive number")

    shiny_rate = config.get("shiny_rate")
    if isinstance(shiny_rate, bool) or not isinstance(shiny_rate, int) or shiny_rate <= 0:
        raise ValueError("shiny_rate must be a positive integer")

    rarity_weights = config.get("rarity_weights")
    if not isinstance(rarity_weights, dict) or not rarity_weights:
        raise ValueError("rarity_weights must be a non-empty object")

    has_positive_weight = False
    for rarity, weight in rarity_weights.items():
        if not isinstance(rarity, str) or not rarity.strip():
            raise ValueError("rarity_weights keys must be non-empty strings")
        if isinstance(weight, bool) or not isinstance(weight, numbers.Real) or weight < 0:
            raise ValueError("rarity_weights values must be non-negative numbers")
        has_positive_weight = has_positive_weight or weight > 0
    if not has_positive_weight:
        raise ValueError("rarity_weights must include at least one positive weight")

    pokemon_data_files = config.get("pokemon_data_files")
    if not isinstance(pokemon_data_files, dict) or not pokemon_data_files:
        raise ValueError("pokemon_data_files must be a non-empty object")
    for generation, path_value in pokemon_data_files.items():
        if not isinstance(generation, str) or not generation.strip():
            raise ValueError("pokemon_data_files keys must be non-empty strings")
        if not isinstance(path_value, str) or not path_value.strip():
            raise ValueError("pokemon_data_files values must be non-empty strings")

    _require_path_string(config, "save_data_file")
    _require_path_string(config, "background_image")

    for key in ("mute_audio", "borderless_mode"):
        if not isinstance(config.get(key), bool):
            raise ValueError(f"{key} must be a boolean")


def load_config():
    """Load configuration from file, merge with defaults, and validate required data files."""
    _create_directories()

    user_config = _load_user_config()
    config = {
        **deepcopy(DEFAULT_RUNTIME_CONFIG),
        **deepcopy(DEFAULT_USER_SETTINGS),
        **user_config,
    }
    _validate_config(config)

    config["background_image"] = paths.normalize_path_value(config["background_image"])
    config["save_data_file"] = paths.normalize_path_value(config["save_data_file"])
    config["pokemon_data_files"] = {
        gen: paths.normalize_path_value(path)
        for gen, path in config["pokemon_data_files"].items()
    }

    config["save_data_file"] = str(paths.resolve_config_path(config["save_data_file"]))

    config["pokemon_data_files"] = {
        gen: str(paths.resolve_asset_path(path))
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
