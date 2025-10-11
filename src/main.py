"""IdleMon - Pokemon encounter simulator with shiny hunting"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from config_loader import load_config, check_file_exists, get_base_path, PROJECT_ROOT
from data_manager import DataManager
from audio_manager import AudioManager
from ui_manager import UIManager
from game_controller import GameController
from settings_dialog import SettingsDialog

# Print startup info
print("Starting IdleMon...")
print(f"Executable path: {sys.executable}")
print(f"Working directory: {Path.cwd()}")

# Initialize configuration and managers
config = load_config()
data_manager = DataManager(config)


class IdleMonWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IdleMon")

        # Store borderless mode setting
        self.borderless_mode = config["borderless_mode"]
        self.shiny_paused = False  # Track if hunt is paused due to shiny

        # Setup borderless transparent window if enabled
        if self.borderless_mode:
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool
            )
            self.setAttribute(Qt.WA_TranslucentBackground)
            # Variables for drag functionality
            self.drag_position = None

            # Create system tray icon
            self._create_tray_icon()

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
        self.ui = UIManager(self, PROJECT_ROOT, background_path, self.borderless_mode)
        self.ui.setup_ui()

        # Connect signals
        self._connect_signals()

        # Initialize game state
        shiny_count = self.game.initialize_shiny_count()
        self.ui.update_shiny_count(shiny_count)

        # Connect continue button (only in normal mode)
        if not self.borderless_mode:
            self.ui.continue_button.clicked.connect(self.continue_hunt)
            # Connect settings button
            self.ui.settings_button.clicked.connect(self.open_settings)

        # Start game
        self.game.start_timer()
        self.game.start_encounter_loop()

    def _create_tray_icon(self):
        """Create system tray icon for borderless mode"""
        # Create tray icon (using a simple approach without icon file for now)
        self.tray_icon = QSystemTrayIcon(self)

        # Create tray menu
        tray_menu = QMenu()

        # Add exit action
        exit_action = tray_menu.addAction("Exit IdleMon")
        exit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("IdleMon - Pokemon Desktop Pet")
        self.tray_icon.show()

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

        # Mark shiny paused for borderless mode
        if self.borderless_mode:
            self.shiny_paused = True

    def continue_hunt(self):
        """Handle continue button click"""
        # Play sound
        self.audio.play_continue_sound()

        # Reset game state
        self.game.reset_encounters()
        self.ui.update_encounter_count(0)

        # Hide button
        self.ui.hide_continue_button()

        # Clear shiny paused state
        if self.borderless_mode:
            self.shiny_paused = False

        # Restart game
        self.game.reset_timer()
        self.game.start_encounter_loop()

    def open_settings(self):
        """Open settings dialog"""
        config_file_path = PROJECT_ROOT / "config.json"
        dialog = SettingsDialog(config, str(config_file_path), self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self, new_config):
        """Handle settings changes"""
        # Update global config (shallow update for immediate changes)
        global config

        # Apply immediate changes (things that don't require restart)
        if 'mute_audio' in new_config and new_config['mute_audio'] != config.get('mute_audio'):
            # Update audio manager
            self.audio.set_mute(new_config['mute_audio'])
            config['mute_audio'] = new_config['mute_audio']

        if 'encounter_delay' in new_config and new_config['encounter_delay'] != config.get('encounter_delay'):
            # Update game controller's encounter delay
            self.game.encounter_delay = new_config['encounter_delay']
            config['encounter_delay'] = new_config['encounter_delay']

        if 'shiny_rate' in new_config and new_config['shiny_rate'] != config.get('shiny_rate'):
            # Update game controller's shiny rate
            self.game.shiny_rate = new_config['shiny_rate']
            config['shiny_rate'] = new_config['shiny_rate']

        # Note: background_image and borderless_mode require restart
        # These are already handled by the dialog showing a restart message

    def mousePressEvent(self, event):
        """Handle mouse press for dragging in borderless mode"""
        if self.borderless_mode and event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging in borderless mode"""
        if self.borderless_mode and event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        """Handle window close"""
        self.game.stop_timer()

        # Clean up tray icon if in borderless mode
        if self.borderless_mode and hasattr(self, 'tray_icon'):
            self.tray_icon.hide()

        event.accept()
        # Force application quit
        QApplication.quit()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = IdleMonWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
