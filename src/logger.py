"""Logging module for errors and shiny encounters"""
import os
import logging
from pathlib import Path
from config_loader import get_base_path


class LogManager:
    """Manages application logging"""

    def __init__(self):
        base_path = get_base_path()
        # Setup log directory
        self.logs_dir = base_path / "logs"
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
        if os.path.exists(self.shiny_log_path):
            with open(self.shiny_log_path, 'r') as f:
                for line in f:
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
            # Write updated encounters to log file
            with open(self.shiny_log_path, 'w', encoding='utf-8') as f:
                for name, data in sorted(self.shiny_encounters.items()):
                    f.write(f"{name} | {data['rarity']} | {data['count']}\n")
        except Exception as e:
            self.error_logger.error(f"Error writing to shiny log: {str(e)}")
            return True  # Return success even if logging failed

# Create global logger instance
logger = LogManager() 