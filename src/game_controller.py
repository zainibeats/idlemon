"""Game controller module for managing game state and encounters"""
import random
import time
from PySide6.QtCore import QObject, QTimer, Signal

# Game constants
NEARBY_SHINY_HINT_DIVISOR = 5  # 1 in (shiny_rate // 5) chance to show nearby hint


class GameSignals(QObject):
    """Signals for UI updates"""
    update_encounter = Signal(str, str, bool, str)  # pokemon_name, rarity, is_shiny, gif_path
    update_counter = Signal(int)
    update_timer = Signal(int)
    shiny_found = Signal(str, str)  # pokemon_name, rarity


class GameController:
    """Controls game logic, state, and encounter system"""

    def __init__(self, config, data_manager, logger):
        """
        Initialize game controller

        Args:
            config: Game configuration dictionary
            data_manager: DataManager instance
            logger: LogManager instance
        """
        self.config = config
        self.data_manager = data_manager
        self.logger = logger

        # Game settings
        self.encounter_delay = config["encounter_delay"]
        self.rarity_weights = config["rarity_weights"]
        self.shiny_rate = config["shiny_rate"]

        # Game state
        self.total_encounters = 0
        self.total_shiny_found = 0
        self.shiny_found_flag = False
        self.elapsed_time = 0
        self.start_time = None
        self.timer_running = False

        # Setup signals
        self.signals = GameSignals()

        # Qt-native timers keep game state on the GUI event loop.
        self.timer = QTimer(self.signals)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_timer)

        self.encounter_timer = QTimer(self.signals)
        self.encounter_timer.setInterval(max(1, int(self.encounter_delay * 1000)))
        self.encounter_timer.timeout.connect(self._run_encounter)
        self.pokemon_data = {}
        self.pokemon_catalog = []
        self.weights = []

    def initialize_shiny_count(self):
        """Load shiny count from saved data"""
        self.total_shiny_found = self.data_manager.load_shiny_count()
        return self.total_shiny_found

    def update_shiny_count(self):
        """Increment and save shiny count"""
        self.total_shiny_found += 1
        self.data_manager.save_shiny_count(self.total_shiny_found)
        return self.total_shiny_found

    def check_shiny(self):
        """
        Determine if encounter is shiny

        Returns:
            bool: True if shiny encounter
        """
        if random.randint(1, self.shiny_rate) == 1:
            return True

        # Easter egg: occasionally record that a shiny is nearby.
        hint_rate = max(1, self.shiny_rate // NEARBY_SHINY_HINT_DIVISOR)
        if random.randint(1, hint_rate) == 1:
            self.logger.log_info("You hear a shiny Pokemon nearby...")

        return False

    def start_timer(self):
        """Start the elapsed time timer"""
        self.start_time = time.time()
        self.timer_running = True
        if not self.timer.isActive():
            self.timer.start()

    def stop_timer(self):
        """Stop the elapsed time timer"""
        self.timer_running = False
        self.timer.stop()

    def reset_timer(self):
        """Reset and restart the timer"""
        self.elapsed_time = 0
        self.start_time = time.time()
        self.signals.update_timer.emit(self.elapsed_time)
        if not self.timer_running:
            self.start_timer()

    def _update_timer(self):
        """Update elapsed time while the timer is active."""
        if self.start_time is None:
            return

        self.elapsed_time = int(time.time() - self.start_time)
        self.signals.update_timer.emit(self.elapsed_time)

    def reset_encounters(self):
        """Reset encounter counter"""
        self.total_encounters = 0
        self.shiny_found_flag = False

    def start_encounter_loop(self):
        """Start the Pokemon encounter timer."""
        if self.encounter_timer.isActive():
            return

        self.pokemon_catalog = self.data_manager.load_pokemon_catalog()
        if not self.pokemon_catalog:
            self.logger.log_error("No Pokemon data available. Exiting encounter loop.")
            return

        self.pokemon_data = {
            pokemon["name"]: pokemon["rarity"]
            for pokemon in self.pokemon_catalog
        }
        self.weights = [
            self.rarity_weights.get(pokemon["rarity"], 0)
            for pokemon in self.pokemon_catalog
        ]
        self.encounter_timer.start()

    def stop_encounter_loop(self):
        """Stop the Pokemon encounter timer."""
        self.encounter_timer.stop()

    def stop(self):
        """Stop all active game timers."""
        self.stop_timer()
        self.stop_encounter_loop()

    def _run_encounter(self):
        """Run a single Pokemon encounter."""
        if self.shiny_found_flag:
            self.stop_encounter_loop()
            return

        self.total_encounters += 1
        self.signals.update_counter.emit(self.total_encounters)

        pokemon = random.choices(self.pokemon_catalog, weights=self.weights, k=1)[0]
        pokemon_name = pokemon["name"]
        pokemon_rarity = pokemon["rarity"]
        is_shiny = self.check_shiny()
        gif_path = pokemon["shiny_gif"] if is_shiny else pokemon["normal_gif"]

        self.signals.update_encounter.emit(pokemon_name, pokemon_rarity, is_shiny, str(gif_path))

        if is_shiny:
            self.shiny_found_flag = True
            self.stop()
            self.signals.shiny_found.emit(pokemon_name, pokemon_rarity)
            self.logger.log_info(
                f"Found shiny {pokemon_name} after {self.total_encounters} encounters."
            )

    def handle_shiny_found(self, pokemon_name, rarity):
        """
        Handle shiny encounter

        Args:
            pokemon_name: Name of shiny Pokemon
            rarity: Rarity tier
        """
        # Update count
        self.update_shiny_count()

        # Log the shiny
        try:
            self.data_manager.log_shiny(pokemon_name, rarity)
        except Exception as e:
            self.logger.log_error(f"Error logging shiny: {str(e)}")
