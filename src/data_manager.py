"""Data management module for Pokemon data and save files"""
import json
import os
from pathlib import Path


class DataManager:
    """Manages Pokemon data and save files"""

    def __init__(self, config, logger):
        self.logger = logger
        self.save_data_file = Path(config["save_data_file"])
        self.pokemon_data_files = {
            gen: Path(path)
            for gen, path in config["pokemon_data_files"].items()
        }
        self.pokemon_data_cache = None

    def _default_save_data(self):
        """Return an empty save data structure."""
        return {
            "version": 1,
            "total_shiny_found": 0,
            "shinies": {},
        }

    def _load_save_data(self):
        """Load save data from JSON, resetting invalid files to defaults."""
        if not self.save_data_file.exists():
            save_data = self._default_save_data()
            self._write_save_data(save_data)
            return save_data

        try:
            save_data = json.loads(self.save_data_file.read_text(encoding="utf-8"))
            if not isinstance(save_data, dict):
                raise ValueError("save data must be a JSON object")

            save_data.setdefault("version", 1)
            if not isinstance(save_data.get("total_shiny_found"), int):
                raise ValueError("total_shiny_found must be an integer")
            if save_data["total_shiny_found"] < 0:
                raise ValueError("total_shiny_found cannot be negative")
            if not isinstance(save_data.get("shinies"), dict):
                raise ValueError("shinies must be an object")
            for name, shiny in save_data["shinies"].items():
                if not isinstance(name, str) or not name:
                    raise ValueError("shiny names must be non-empty strings")
                if not isinstance(shiny, dict):
                    raise ValueError(f"shiny entry for {name} must be an object")
                if not isinstance(shiny.get("rarity"), str):
                    raise ValueError(f"rarity for {name} must be a string")
                if not isinstance(shiny.get("count"), int) or shiny["count"] < 1:
                    raise ValueError(f"count for {name} must be a positive integer")

            return save_data
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.log_error(f"Error loading save data: {e}")
            self.logger.log_warning(f"{self.save_data_file} is corrupted. Resetting save data.")
            save_data = self._default_save_data()
            self._write_save_data(save_data)
            return save_data

    def _write_save_data(self, save_data):
        """Atomically write save data to JSON."""
        self.save_data_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.save_data_file.with_name(f"{self.save_data_file.name}.tmp")
        temp_file.write_text(
            json.dumps(save_data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temp_file, self.save_data_file)

    def load_shiny_count(self):
        """Load total shiny count from save data."""
        return self._load_save_data()["total_shiny_found"]

    def save_shiny_count(self, count):
        """Save shiny count to save data."""
        if not isinstance(count, int) or count < 0:
            raise ValueError("count must be a non-negative integer")

        save_data = self._load_save_data()
        save_data["total_shiny_found"] = count
        self._write_save_data(save_data)

    def log_shiny(self, pokemon_name, rarity):
        """Record shiny Pokemon encounter in save data."""
        save_data = self._load_save_data()
        shinies = save_data["shinies"]

        if pokemon_name in shinies:
            shinies[pokemon_name]["count"] += 1
            shinies[pokemon_name]["rarity"] = rarity
        else:
            shinies[pokemon_name] = {"rarity": rarity, "count": 1}

        self._write_save_data(save_data)

    def get_all_shinies(self):
        """Get all recorded shiny encounters."""
        return self._load_save_data()["shinies"].copy()

    def save_path(self):
        """Return the current save data file path."""
        return self.save_data_file

    def load_pokemon_data(self):
        """Load and cache Pokemon data from all generation files"""
        if self.pokemon_data_cache is not None:
            return self.pokemon_data_cache

        pokemon_data = {}
        for gen, file_path in self.pokemon_data_files.items():
            try:
                for line in file_path.read_text(encoding="utf-8").splitlines():
                    try:
                        name, rarity = line.strip().split(',')
                        pokemon_data[name] = rarity
                    except ValueError:
                        self.logger.log_error(f"Invalid entry in {file_path}: {line.strip()}")
            except Exception as e:
                self.logger.log_error(f"Error loading Pokemon data for {gen}: {e}")

        self.pokemon_data_cache = pokemon_data
        return pokemon_data
