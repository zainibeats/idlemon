"""IdleMon - Pokemon encounter simulator with shiny hunting"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
import paths
from config_loader import ConfigError, load_config
from data_manager import DataManager
from audio_manager import AudioManager
from ui_manager import UIManager
from game_controller import GameController
from settings_dialog import SettingsDialog
from collection_window import CollectionWindow
from logger import LogManager
from version import APP_VERSION


class IdleMonWindow(QMainWindow):
    """Main application window"""

    def __init__(self, config, data_manager, logger):
        super().__init__()
        self.setWindowTitle(f"IdleMon {APP_VERSION}")

        # Store config and settings
        self.config = config
        self.logger = logger
        self.data_manager = data_manager
        self.borderless_mode = config["borderless_mode"]
        self.shiny_paused = False
        self.collection_window = None

        # Setup borderless transparent window if enabled
        if self.borderless_mode:
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool
            )
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.drag_position = None
            self._create_tray_icon()

        # Initialize managers
        self.game = GameController(config, data_manager, self.logger)
        self.audio = AudioManager(paths.PROJECT_ROOT, config["mute_audio"], self.logger)

        # Setup background path
        requested_background_path = paths.resolve_asset_path(config["background_image"])
        background_path = paths.resolve_background_path(config["background_image"])
        if background_path != requested_background_path:
            self.logger.log_warning(
                f"Could not find background image at {requested_background_path}; using default."
            )

        # Initialize UI
        self.ui = UIManager(
            self,
            paths.PROJECT_ROOT,
            background_path,
            self.borderless_mode,
            self.logger,
        )
        self.ui.setup_ui()

        # Connect signals
        self._connect_signals()

        # Initialize game state
        shiny_count = self.game.initialize_shiny_count()
        self.ui.update_shiny_count(shiny_count)

        # Connect buttons and labels (only in normal mode)
        if not self.borderless_mode:
            self.ui.continue_button.clicked.connect(self.continue_hunt)
            self.ui.settings_button.clicked.connect(self.open_settings)
            self.ui.enable_shiny_label_click(self.open_collection_window)

        # Start game
        self.game.start_timer()
        self.game.start_encounter_loop()

    def _create_tray_icon(self):
        """Create system tray icon for borderless mode"""
        self.tray_icon = QSystemTrayIcon(self)
        tray_menu = QMenu()
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

    def on_encounter_update(self, pokemon_name, rarity, is_shiny, gif_path):
        self.ui.update_encounter_display(pokemon_name, rarity, is_shiny, gif_path)

    def on_counter_update(self, count):
        self.ui.update_encounter_count(count)

    def on_timer_update(self, seconds):
        self.ui.update_timer(seconds)

    def on_shiny_found(self, pokemon_name, rarity):
        """Handle shiny encounter"""
        self.audio.play_shiny_sound()
        self.game.handle_shiny_found(pokemon_name, rarity)
        self.ui.update_shiny_count(self.game.total_shiny_found)
        self.ui.show_continue_button()

        if self.borderless_mode:
            self.shiny_paused = True

    def continue_hunt(self):
        """Handle continue button click"""
        self.audio.play_continue_sound()
        self.game.reset_encounters()
        self.ui.update_encounter_count(0)
        self.ui.hide_continue_button()

        if self.borderless_mode:
            self.shiny_paused = False

        self.game.reset_timer()
        self.game.start_encounter_loop()

    def open_settings(self):
        """Open settings dialog"""
        config_file_path = paths.get_config_file()
        dialog = SettingsDialog(self.config, str(config_file_path), paths.PROJECT_ROOT, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def open_collection_window(self):
        """Open or bring to front the shiny collection window"""
        if self.collection_window and self.collection_window.isVisible():
            self.collection_window.raise_()
            self.collection_window.activateWindow()
        else:
            self.collection_window = CollectionWindow(self.data_manager, paths.PROJECT_ROOT, self)
            self.collection_window.show()

    def on_settings_changed(self, new_config):
        """Handle settings changes that don't require restart"""
        if 'mute_audio' in new_config and new_config['mute_audio'] != self.config.get('mute_audio'):
            self.audio.set_mute(new_config['mute_audio'])
            self.config['mute_audio'] = new_config['mute_audio']

    def mousePressEvent(self, event):
        if self.borderless_mode and event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.borderless_mode and event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        self.game.stop()
        if self.borderless_mode and hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        event.accept()
        QApplication.quit()


def main():
    """Main entry point"""
    logger = LogManager(paths.get_logs_dir())
    logger.log_info("Starting IdleMon.")
    logger.log_info(f"Executable path: {sys.executable}")
    logger.log_info(f"Working directory: {Path.cwd()}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    try:
        config = load_config(logger)
    except ConfigError as e:
        QMessageBox.critical(None, "IdleMon Startup Error", str(e))
        sys.exit(1)

    data_manager = DataManager(config, logger)

    window = IdleMonWindow(config, data_manager, logger)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
