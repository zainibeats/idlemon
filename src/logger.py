"""Logging module for errors and shiny encounters"""
import logging
from pathlib import Path


class LogManager:
    """Manages application logging"""

    def __init__(self, logs_dir):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

        # Configure error logging
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(self.logs_dir / 'error.log')
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.error_logger.addHandler(error_handler)

        # Initialize shiny encounter tracking
        self.shiny_log_path = self.logs_dir / 'shinies_encountered.txt'
        self.shiny_encounters = self._load_shiny_encounters()

    def _load_shiny_encounters(self):
        """Load previous shiny encounters from log file"""
        encounters = {}
        if self.shiny_log_path.exists():
            for line in self.shiny_log_path.read_text(encoding='utf-8').splitlines():
                try:
                    name, rarity, count = line.strip().split(' | ')
                    encounters[name] = {'rarity': rarity, 'count': int(count)}
                except ValueError:
                    self.error_logger.error(f"Invalid line in shiny log: {line.strip()}")
        return encounters

    def log_error(self, message):
        """Log error message to error.log"""
        self.error_logger.error(message)

    def log_shiny(self, pokemon_name, rarity):
        """Record shiny Pokemon encounter in log file"""
        # Update encounter count
        if pokemon_name in self.shiny_encounters:
            self.shiny_encounters[pokemon_name]['count'] += 1
        else:
            self.shiny_encounters[pokemon_name] = {'rarity': rarity, 'count': 1}

        try:
            lines = [f"{name} | {data['rarity']} | {data['count']}"
                     for name, data in sorted(self.shiny_encounters.items())]
            self.shiny_log_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        except Exception as e:
            self.error_logger.error(f"Error writing to shiny log: {e}")

    def get_all_shinies(self):
        """
        Get all recorded shiny encounters

        Returns:
            dict: Dictionary of shiny encounters with format:
                  {pokemon_name: {'rarity': str, 'count': int}}
        """
        return self.shiny_encounters.copy()