"""IdleMon - Pokemon encounter simulator with shiny hunting"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

from config_loader import load_config, check_file_exists, get_base_path
from data_manager import DataManager
from audio_manager import AudioManager
from ui_manager import UIManager
from game_controller import GameController

# Print startup info
print("Starting IdleMon...")
print(f"Executable path: {sys.executable}")
print(f"Working directory: {Path.cwd()}")

# Get application root path
PROJECT_ROOT = get_base_path()

# Initialize configuration and managers
config = load_config()
data_manager = DataManager(config)


class IdleMonWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IdleMon")

        # Initialize managers
        self.game = GameController(config, data_manager)
        self.audio = AudioManager(PROJECT_ROOT, config["mute_audio"])

        # Setup background path
        background_image_path = config["background_image"]
        if not Path(background_image_path).is_absolute():
            background_path = PROJECT_ROOT / background_image_path
        else:
            background_path = Path(background_image_path)

        # Fallback to default if not found
        if not check_file_exists(background_path):
            print(f"Warning: Could not find background image at {background_path}")
            background_path = PROJECT_ROOT / "assets" / "images" / "default_background.jpg"

        # Initialize UI
        self.ui = UIManager(self, PROJECT_ROOT, background_path)
        self.ui.setup_ui()

        # Connect signals
        self._connect_signals()

        # Initialize game state
        shiny_count = self.game.initialize_shiny_count()
        self.ui.update_shiny_count(shiny_count)

        # Connect continue button
        self.ui.continue_button.clicked.connect(self.continue_hunt)

        # Start game
        self.game.start_timer()
        self.game.start_encounter_loop()

    def _connect_signals(self):
        """Connect game signals to UI updates"""
        self.game.signals.update_encounter.connect(self.on_encounter_update)
        self.game.signals.update_counter.connect(self.on_counter_update)
        self.game.signals.update_timer.connect(self.on_timer_update)
        self.game.signals.shiny_found.connect(self.on_shiny_found)

    def on_encounter_update(self, pokemon_name, rarity, is_shiny):
        """Handle encounter update"""
        self.ui.update_encounter_display(pokemon_name, rarity, is_shiny)

    def on_counter_update(self, count):
        """Handle encounter counter update"""
        self.ui.update_encounter_count(count)

    def on_timer_update(self, seconds):
        """Handle timer update"""
        self.ui.update_timer(seconds)

    def on_shiny_found(self, pokemon_name, rarity):
        """Handle shiny encounter"""
        # Play sound
        self.audio.play_shiny_sound()

        # Update game state
        self.game.handle_shiny_found(pokemon_name, rarity)

        # Update UI
        new_count = self.game.total_shiny_found
        self.ui.update_shiny_count(new_count)
        self.ui.show_continue_button()

    def continue_hunt(self):
        """Handle continue button click"""
        # Play sound
        self.audio.play_continue_sound()

        # Reset game state
        self.game.reset_encounters()
        self.ui.update_encounter_count(0)

        # Hide button
        self.ui.hide_continue_button()

        # Restart game
        self.game.reset_timer()
        self.game.start_encounter_loop()

    def closeEvent(self, event):
        """Handle window close"""
        self.game.stop_timer()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = IdleMonWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
