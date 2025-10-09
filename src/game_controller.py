"""Game controller module for managing game state and encounters"""
import random
import time
import threading
from colorama import Fore, Style
from PySide6.QtCore import QObject, Signal

from logger import logger


class GameSignals(QObject):
    """Signals for thread-safe UI updates"""
    update_encounter = Signal(str, str, bool)  # pokemon_name, rarity, is_shiny
    update_counter = Signal(int)
    update_timer = Signal(int)
    shiny_found = Signal(str, str)  # pokemon_name, rarity


class GameController:
    """Controls game logic, state, and encounter system"""

    def __init__(self, config, data_manager):
        """
        Initialize game controller

        Args:
            config: Game configuration dictionary
            data_manager: DataManager instance
        """
        self.config = config
        self.data_manager = data_manager

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
        shiny_value = random.randint(1, self.shiny_rate)
        if shiny_value == 1:
            return True
        elif random.randint(1, self.shiny_rate // 5) == 1:
            print(Fore.MAGENTA + "You hear a shiny Pokémon nearby..." + Style.RESET_ALL)
        return False

    def start_timer(self):
        """Start the elapsed time timer"""
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self._update_timer_loop, daemon=True).start()

    def stop_timer(self):
        """Stop the elapsed time timer"""
        self.timer_running = False

    def reset_timer(self):
        """Reset and restart the timer"""
        self.elapsed_time = 0
        self.start_time = time.time()
        if not self.timer_running:
            self.start_timer()

    def _update_timer_loop(self):
        """Timer update loop (runs in background thread)"""
        while self.timer_running:
            if self.start_time is not None:
                self.elapsed_time += time.time() - self.start_time
                self.start_time = time.time()
            self.signals.update_timer.emit(int(self.elapsed_time))
            time.sleep(1)

    def reset_encounters(self):
        """Reset encounter counter"""
        self.total_encounters = 0
        self.shiny_found_flag = False

    def start_encounter_loop(self):
        """Start the Pokemon encounter loop in a background thread"""
        threading.Thread(target=self._encounter_loop, daemon=True).start()

    def _encounter_loop(self):
        """Main encounter loop (runs in background thread)"""
        # Load Pokemon data
        pokemon_data = self.data_manager.load_pokemon_data()
        if not pokemon_data:
            print("No Pokémon data available. Exiting encounter loop.")
            return

        # Prepare weighted selection
        pokemon_list = list(pokemon_data.keys())
        weights = [self.rarity_weights.get(rarity, 0) for rarity in pokemon_data.values()]

        # Run encounter loop until shiny found
        while not self.shiny_found_flag:
            time.sleep(self.encounter_delay)
            self.total_encounters += 1
            self.signals.update_counter.emit(self.total_encounters)

            # Select random Pokemon based on rarity weights
            pokemon_name = random.choices(pokemon_list, weights=weights, k=1)[0]
            pokemon_rarity = pokemon_data[pokemon_name]

            # Check if shiny
            is_shiny = self.check_shiny()

            # Emit update signal
            self.signals.update_encounter.emit(pokemon_name, pokemon_rarity, is_shiny)

            if is_shiny:
                self.shiny_found_flag = True
                self.stop_timer()
                self.signals.shiny_found.emit(pokemon_name, pokemon_rarity)
                print(Fore.YELLOW + f"Congrats!!! You found a shiny {pokemon_name} after {self.total_encounters} encounters!" + Style.RESET_ALL)
            else:
                print(f"You encountered a wild {pokemon_name}!")

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
            logger.log_shiny(pokemon_name, rarity)
        except Exception as e:
            logger.log_error(f"Error logging shiny: {str(e)}")
