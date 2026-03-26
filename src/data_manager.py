"""Data management module for Pokemon data and save files"""
import base64
from pathlib import Path


class DataManager:
    """Manages Pokemon data and save files"""

    def __init__(self, config, logger):
        self.logger = logger
        self.shiny_count_file = Path(config["shiny_count_file"])
        self.pokemon_data_files = {
            gen: Path(path)
            for gen, path in config["pokemon_data_files"].items()
        }
        self.pokemon_data_cache = None

    def load_shiny_count(self):
        """Load total shiny count from file, reset to 0 if corrupted or missing"""
        if self.shiny_count_file.exists():
            try:
                encoded = self.shiny_count_file.read_text().strip()
                return int(base64.b64decode(encoded).decode("utf-8"))
            except (ValueError, base64.binascii.Error) as e:
                self.logger.log_error(f"Error loading shiny count: {e}")
                print(f"Warning: {self.shiny_count_file} is corrupted. Resetting to 0.")
        else:
            logger.log_error(f"Shiny count file missing: {self.shiny_count_file}")
            print(f"Warning: {self.shiny_count_file} is missing. Creating new file.")

        self.save_shiny_count(0)
        return 0

    def save_shiny_count(self, count):
        """Save shiny count to file using base64 encoding"""
        encoded = base64.b64encode(str(count).encode("utf-8")).decode("utf-8")
        self.shiny_count_file.write_text(encoded)

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
