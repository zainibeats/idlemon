"""UI management module for Qt interface"""
from pathlib import Path
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QMenu
from PySide6.QtCore import Qt, QPoint, QRect, QSize, Signal
from PySide6.QtGui import QPixmap, QMovie, QRegion
from ui_colors import UIColors
from ui_styles import button_style, transparent_label_style
from utils import find_pokemon_gif

# UI Constants
GIF_SCALE_FACTOR = 1.5
GIF_ANIMATION_SPEED = 100
STATS_PANEL_WIDTH = 230
BACKGROUND_HEIGHT = 500

# Borderless desktop pet mode. The canvas is fixed and large enough for the biggest
# scaled sprite (308x234) so no Pokemon is clipped, and the sprite is centred in it so
# the pet does not jump when a larger or smaller species appears. Only the sprite plus
# a small grab margin is unmasked, so the rest of the canvas stays click-through.
BORDERLESS_CANVAS_SIZE = QSize(340, 280)
BORDERLESS_GRAB_PADDING = 10


class ClickableLabel(QLabel):
    """QLabel that emits a clicked signal when clicked"""
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class UIManager:
    """Manages the Qt user interface components"""

    def __init__(self, main_window, background_path, borderless_mode=False, logger=None):
        """
        Initialize UI manager

        Args:
            main_window: The main QMainWindow instance
            background_path: Path to background image
            borderless_mode: Whether to use borderless transparent mode
            logger: Optional LogManager instance
        """
        self.window = main_window
        self.background_path = Path(background_path)
        self.borderless_mode = borderless_mode
        self.logger = logger

        # UI components (will be created in setup)
        self.info_label = None
        self.encounter_label = None
        self.shiny_label = None
        self.stats_label = None
        self.pokemon_label = None
        self.pokemon_movie = None
        self.continue_button = None
        self.settings_button = None
        self.foreground_layout = None

    def setup_ui(self):
        """Setup the main UI with all components"""
        if self.borderless_mode:
            # Borderless mode: transparent background, only pokemon gif
            central_widget = QWidget()
            central_widget.setStyleSheet("background: transparent;")
            self.window.setCentralWidget(central_widget)

            # Simple layout for pokemon only
            self.foreground_layout = QVBoxLayout(central_widget)
            self.foreground_layout.setContentsMargins(0, 0, 0, 0)

            # Create Pokemon display area
            self._create_pokemon_display()

            # A fixed canvas keeps the sprite's centre stable across species changes.
            self.window.setFixedSize(BORDERLESS_CANVAS_SIZE)
            self._update_borderless_grab_region(QSize(0, 0))
        else:
            # Normal mode: background image with stats
            # Load and scale background
            background_pixmap = QPixmap(str(self.background_path))
            background_pixmap = background_pixmap.scaledToHeight(BACKGROUND_HEIGHT, Qt.SmoothTransformation)

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

    def _create_stats_panel(self):
        """Create the stats display panel"""
        stats_widget = QWidget()
        stats_widget.setFixedWidth(STATS_PANEL_WIDTH)
        stats_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {UIColors.BG_DARK};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(5)

        # Info label
        self.info_label = QLabel("Walking through the Pokemon world...")
        self.info_label.setStyleSheet(transparent_label_style(font_size=12, bold=True))
        self.info_label.setWordWrap(True)
        self.info_label.setFixedWidth(STATS_PANEL_WIDTH)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        stats_layout.addWidget(self.info_label)

        # Encounter counter
        self.encounter_label = QLabel("Encounters: 0")
        self.encounter_label.setStyleSheet(transparent_label_style())
        stats_layout.addWidget(self.encounter_label)

        # Shiny counter (clickable)
        self.shiny_label = ClickableLabel("Shiny Pokémon Found: 0")
        self.shiny_label.setStyleSheet(transparent_label_style() + f"""
            QLabel:hover {{
                color: {UIColors.TEXT_SHINY};
                text-decoration: underline;
            }}
        """)
        self.shiny_label.setCursor(Qt.PointingHandCursor)
        self.shiny_label.setToolTip("Click to view your shiny collection")
        stats_layout.addWidget(self.shiny_label)

        # Timer
        self.stats_label = QLabel("Time Elapsed: 00:00")
        self.stats_label.setStyleSheet(transparent_label_style())
        stats_layout.addWidget(self.stats_label)

        # Settings button
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_SECONDARY,
                UIColors.PRIMARY_BLUE,
                pressed_color=UIColors.PRIMARY_BLUE,
                pressed_opacity=0.8,
                font_size=10,
                padding="5px",
            ) + """
            QPushButton {
                margin-top: 5px;
            }
            """
        )
        stats_layout.addWidget(self.settings_button)

        self.foreground_layout.addWidget(stats_widget, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.foreground_layout.addStretch()

    def _create_pokemon_display(self):
        """Create the Pokemon GIF display area"""
        self.pokemon_label = QLabel()
        self.pokemon_label.setAlignment(Qt.AlignCenter)
        self.pokemon_label.setStyleSheet("background: transparent;")

        # A single QMovie is reused for every encounter. QLabel.setMovie() keeps a
        # reference to each movie it is handed, so building one per encounter would
        # hold every GIF file open until the app runs out of file descriptors.
        self.pokemon_movie = QMovie(self.pokemon_label)
        self.pokemon_movie.setSpeed(GIF_ANIMATION_SPEED)
        self.pokemon_label.setMovie(self.pokemon_movie)

        # Enable context menu for borderless mode
        if self.borderless_mode:
            self.pokemon_label.setContextMenuPolicy(Qt.CustomContextMenu)
            self.pokemon_label.customContextMenuRequested.connect(self._show_context_menu)

        self.foreground_layout.addWidget(self.pokemon_label, alignment=Qt.AlignCenter)
        if not self.borderless_mode:
            # Borderless mode shows only the sprite, so it stays centred in the canvas.
            self.foreground_layout.addStretch()

    def _create_continue_button(self):
        """Create the continue hunt button"""
        self.continue_button = QPushButton("Continue Hunt")
        self.continue_button.setMinimumSize(150, 40)
        self.continue_button.setFocusPolicy(Qt.NoFocus)
        self.continue_button.setAutoDefault(False)
        self.continue_button.setDefault(False)
        self.continue_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_PRIMARY,
                UIColors.ACCENT_HOVER,
                pressed_color=UIColors.ACCENT_PRESSED,
                font_size=14,
                border_radius=20,
                padding="10px",
            )
        )
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
        gif_path = find_pokemon_gif(pokemon_name, is_shiny)

        if not gif_path:
            if self.logger is not None:
                self.logger.log_error(f"GIF file not found for {pokemon_name}")
            return

        self.pokemon_movie.stop()
        # Clear any previous scaling so the new GIF's native frame size can be read.
        self.pokemon_movie.setScaledSize(QSize())
        self.pokemon_movie.setFileName(str(gif_path))
        self.pokemon_movie.jumpToFrame(0)

        native_size = self.pokemon_movie.currentPixmap().size()
        if not native_size.isEmpty():
            self.pokemon_movie.setScaledSize(native_size * GIF_SCALE_FACTOR)

        self.pokemon_movie.start()

        if self.borderless_mode:
            self._update_borderless_grab_region(self.pokemon_movie.scaledSize())

    def _update_borderless_grab_region(self, sprite_size):
        """
        Restrict the window to the sprite plus a small grab margin.

        A translucent window is only click-through on Windows, where transparent
        pixels of a layered window pass clicks to the desktop. On X11 and Wayland
        transparency is purely visual and the whole window rectangle still swallows
        input, so the canvas has to be masked down to the sprite explicitly.
        """
        if sprite_size.isEmpty():
            # No sprite yet, so nothing should be grabbable.
            self.window.setMask(QRegion())
            return

        grab_rect = QRect(QPoint(0, 0), sprite_size + QSize(
            2 * BORDERLESS_GRAB_PADDING,
            2 * BORDERLESS_GRAB_PADDING,
        ))
        grab_rect.moveCenter(QRect(QPoint(0, 0), BORDERLESS_CANVAS_SIZE).center())

        self.pokemon_label.setFixedSize(sprite_size)
        self.window.setMask(QRegion(grab_rect))

    def update_encounter_display(self, pokemon_name, rarity, is_shiny):
        """Update the encounter info display"""
        self.display_pokemon_gif(pokemon_name, is_shiny)

        # Skip text updates in borderless mode
        if self.borderless_mode:
            return

        if is_shiny:
            self.info_label.setText(f"{pokemon_name} - {rarity} (Shiny!)")
            self.info_label.setStyleSheet(
                transparent_label_style(UIColors.TEXT_SHINY, font_size=12, bold=True)
            )
        else:
            self.info_label.setText(f"{pokemon_name} - {rarity}")
            self.info_label.setStyleSheet(transparent_label_style(font_size=12, bold=True))

    def update_encounter_count(self, count):
        """Update encounter counter display"""
        if not self.borderless_mode:
            self.encounter_label.setText(f"Encounters: {count}")

    def update_shiny_count(self, count):
        """Update shiny counter display"""
        if not self.borderless_mode:
            self.shiny_label.setText(f"Shiny Pokémon Found: {count}")

    def update_timer(self, seconds):
        """Update timer display"""
        if not self.borderless_mode:
            minutes, secs = divmod(seconds, 60)
            self.stats_label.setText(f"Time Elapsed: {minutes:02}:{secs:02}")

    def show_continue_button(self):
        """Show the continue button"""
        if not self.borderless_mode:
            self.continue_button.show()

    def hide_continue_button(self):
        """Hide the continue button"""
        if not self.borderless_mode:
            self.continue_button.hide()

    def build_context_menu(self):
        """
        Build the borderless-mode context menu.

        The menu is parented to the sprite label on purpose. An unparented popup
        becomes its own top-level surface on Wayland, and clients cannot position
        top-level surfaces, so the compositor drops it in a screen corner.
        """
        menu = QMenu(self.pokemon_label)

        # Add continue hunt option if shiny is paused
        if getattr(self.window, 'shiny_paused', False):
            menu.addAction("Continue Hunt").triggered.connect(self.window.continue_hunt)
            menu.addSeparator()

        menu.addAction("View Collection").triggered.connect(self.window.open_collection_window)
        menu.addAction("⚙ Settings").triggered.connect(self.window.open_settings)

        # Always add exit option
        menu.addSeparator()
        menu.addAction("Exit IdleMon").triggered.connect(self.window.close)

        return menu

    def _show_context_menu(self, position):
        """Show context menu for borderless mode"""
        if not self.borderless_mode:
            return

        # Show menu at cursor position
        self.build_context_menu().exec(self.pokemon_label.mapToGlobal(position))

    def enable_shiny_label_click(self, callback):
        """
        Enable click functionality on the shiny label

        Args:
            callback: Function to call when shiny label is clicked
        """
        if not self.borderless_mode and self.shiny_label:
            self.shiny_label.clicked.connect(callback)
