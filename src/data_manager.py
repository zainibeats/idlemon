"""Data management module for Pokemon data and save files"""
import os
import base64
from pathlib import Path
from config_loader import get_base_path, validate_pokemon_data_file
from logger import logger


class DataManager:
    """Manages Pokemon data and save files"""

    def __init__(self, config):
        """
        Initialize data manager

        Args:
            config: Configuration dictionary
        """
        base_path = get_base_path()
        # Setup file paths
        self.shiny_count_file = base_path / "logs" / "shiny_count.bin"
        self.pokemon_data_files = {
            gen: Path(path)
            for gen, path in config["pokemon_data_files"].items()
        }
        self.pokemon_data_cache = None

    def load_shiny_count(self):
        """Load total shiny count from file, reset to 0 if corrupted or missing"""
        if os.path.exists(self.shiny_count_file):
            with open(self.shiny_count_file, "r") as file:
                try:
                    encoded = file.read().strip()
                    return int(base64.b64decode(encoded).decode("utf-8"))
                except (ValueError, base64.binascii.Error) as e:
                    logger.log_error(f"Error loading shiny count: {str(e)}")
                    print(f"Warning: {self.shiny_count_file} is corrupted. Resetting to 0.")
        else:
            logger.log_error(f"Shiny count file missing: {self.shiny_count_file}")
            print(f"Warning: {self.shiny_count_file} is missing. Creating new file.")
        
        self.save_shiny_count(0)
        return 0

    def save_shiny_count(self, count):
        """Save shiny count to file using base64 encoding"""
        encoded = base64.b64encode(str(count).encode("utf-8")).decode("utf-8")
        with open(self.shiny_count_file, "w") as file:
            file.write(encoded)

    def validate_pokemon_data(self, gen, file_path):
        """Verify Pokemon data file integrity using SHA-256 hash"""
        is_valid = validate_pokemon_data_file(gen, file_path)
        if not is_valid:
            logger.log_error(f"Pokemon data validation failed for {gen}: {file_path}")
        return is_valid

    def load_pokemon_data(self):
        """Load and cache Pokemon data from all generation files"""
        # Return cached data if available
        if self.pokemon_data_cache is not None:
            return self.pokemon_data_cache
        
        pokemon_data = {}
        
        # Load and validate each generation
        for gen, file_path in self.pokemon_data_files.items():
            if not self.validate_pokemon_data(gen, file_path):
                logger.log_error(f"Data validation failed for {gen}")
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        try:
                            name, rarity = line.strip().split(',')
                            pokemon_data[name] = rarity
                        except ValueError:
                            logger.log_error(f"Invalid entry in {file_path}: {line.strip()}")
            except Exception as e:
                logger.log_error(f"Error loading Pokemon data for {gen}: {str(e)}")
            
        # Cache the combined data
        self.pokemon_data_cache = pokemon_data
        return pokemon_data
