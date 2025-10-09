"""UI management module for Qt interface"""
from pathlib import Path
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QMovie


class UIManager:
    """Manages the Qt user interface components"""

    def __init__(self, main_window, project_root, background_path):
        """
        Initialize UI manager

        Args:
            main_window: The main QMainWindow instance
            project_root: Base path for assets
            background_path: Path to background image
        """
        self.window = main_window
        self.project_root = Path(project_root)
        self.background_path = Path(background_path)

        # UI components (will be created in setup)
        self.info_label = None
        self.encounter_label = None
        self.shiny_label = None
        self.stats_label = None
        self.pokemon_label = None
        self.continue_button = None
        self.foreground_layout = None

    def setup_ui(self):
        """Setup the main UI with all components"""
        # Load and scale background
        background_pixmap = QPixmap(str(self.background_path))
        background_pixmap = background_pixmap.scaledToHeight(500, Qt.SmoothTransformation)

        # Create central widget with background
        central_widget = QLabel()
        central_widget.setPixmap(background_pixmap)
        central_widget.setScaledContents(False)
        self.window.setCentralWidget(central_widget)

        # Create foreground layout
        self.foreground_layout = QVBoxLayout(central_widget)
        self.foreground_layout.setContentsMargins(10, 10, 10, 10)

        # Create stats panel
        self._create_stats_panel()

        # Create Pokemon display area
        self._create_pokemon_display()

        # Create continue button
        self._create_continue_button()

        # Set window size based on background
        self.window.setFixedSize(background_pixmap.width(), background_pixmap.height())

        return background_pixmap.width(), background_pixmap.height()

    def _create_stats_panel(self):
        """Create the stats display panel"""
        stats_widget = QWidget()
        stats_widget.setFixedWidth(230)
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(5)

        # Info label
        self.info_label = QLabel("Walking through the Pokemon world...")
        self.info_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                padding: 5px;
            }
        """)
        self.info_label.setWordWrap(True)
        self.info_label.setFixedWidth(230)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        stats_layout.addWidget(self.info_label)

        # Encounter counter
        self.encounter_label = QLabel("Encounters: 0")
        self.encounter_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                background: transparent;
                padding: 5px;
            }
        """)
        stats_layout.addWidget(self.encounter_label)

        # Shiny counter
        self.shiny_label = QLabel("Shiny Pokémon Found: 0")
        self.shiny_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                background: transparent;
                padding: 5px;
            }
        """)
        stats_layout.addWidget(self.shiny_label)

        # Timer
        self.stats_label = QLabel("Time Elapsed: 00:00")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                background: transparent;
                padding: 5px;
            }
        """)
        stats_layout.addWidget(self.stats_label)

        self.foreground_layout.addWidget(stats_widget, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.foreground_layout.addStretch()

    def _create_pokemon_display(self):
        """Create the Pokemon GIF display area"""
        self.pokemon_label = QLabel()
        self.pokemon_label.setAlignment(Qt.AlignCenter)
        self.pokemon_label.setStyleSheet("background: transparent;")
        self.foreground_layout.addWidget(self.pokemon_label, alignment=Qt.AlignCenter)
        self.foreground_layout.addStretch()

    def _create_continue_button(self):
        """Create the continue hunt button"""
        self.continue_button = QPushButton("Continue Hunt")
        self.continue_button.setMinimumSize(150, 40)
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.continue_button.hide()
        self.foreground_layout.addWidget(self.continue_button, alignment=Qt.AlignCenter)
        self.foreground_layout.addStretch()

    def display_pokemon_gif(self, pokemon_name, is_shiny=False):
        """
        Display Pokemon GIF animation

        Args:
            pokemon_name: Name of Pokemon
            is_shiny: Whether to show shiny version
        """
        gif_subdir = "shiny" if is_shiny else "normal"

        # Find GIF in generation directories
        gif_path = None
        for gen in range(1, 6):
            test_path = self.project_root / "assets" / "gifs" / f"gen{gen}" / gif_subdir / f"{pokemon_name}.gif"
            if test_path.exists():
                gif_path = test_path
                break

        if not gif_path:
            print(f"GIF file not found for {pokemon_name}")
            return

        # Create and setup QMovie
        movie = QMovie(str(gif_path))
        movie.setScaledSize(movie.scaledSize() * 1.5)
        movie.setSpeed(100)

        self.pokemon_label.setMovie(movie)
        movie.start()

    def update_encounter_display(self, pokemon_name, rarity, is_shiny):
        """Update the encounter info display"""
        self.display_pokemon_gif(pokemon_name, is_shiny)

        if is_shiny:
            self.info_label.setText(f"{pokemon_name} - {rarity} (Shiny!)")
            self.info_label.setStyleSheet("""
                QLabel {
                    color: gold;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                    padding: 5px;
                }
            """)
        else:
            self.info_label.setText(f"{pokemon_name} - {rarity}")
            self.info_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                    padding: 5px;
                }
            """)

    def update_encounter_count(self, count):
        """Update encounter counter display"""
        self.encounter_label.setText(f"Encounters: {count}")

    def update_shiny_count(self, count):
        """Update shiny counter display"""
        self.shiny_label.setText(f"Shiny Pokémon Found: {count}")

    def update_timer(self, seconds):
        """Update timer display"""
        minutes, secs = divmod(seconds, 60)
        self.stats_label.setText(f"Time Elapsed: {minutes:02}:{secs:02}")

    def show_continue_button(self):
        """Show the continue button"""
        self.continue_button.show()

    def hide_continue_button(self):
        """Hide the continue button"""
        self.continue_button.hide()
