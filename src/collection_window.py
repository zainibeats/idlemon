"""Collection window module for displaying shiny Pokemon collection"""
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QWidget, QGridLayout, QLineEdit, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie
from ui_colors import UIColors
from ui_styles import button_style, combo_box_style, line_edit_style, transparent_label_style
from utils import find_pokemon_gif

# Collection display constants
ITEM_WIDTH = 150
ITEM_HEIGHT = 220
GIF_SIZE = 120
GIF_DISPLAY_SIZE = 100
GRID_SPACING = 15
SCROLL_MARGIN = 20
MIN_COLUMNS = 1
MAX_COLUMNS = 8
DEFAULT_COLUMNS = 4
GIF_ANIMATION_SPEED = 100

RARITY_ORDER = {
    'Very Rare': 0,
    'Rare': 1,
    'Semi-rare': 2,
    'Common': 3,
    'Very Common': 4,
}


def _fit_size(size):
    """Scale a frame size to the tile size while keeping its aspect ratio."""
    scale = min(GIF_DISPLAY_SIZE / size.width(), GIF_DISPLAY_SIZE / size.height())
    return QSize(int(size.width() * scale), int(size.height() * scale))


def _load_first_frame(gif_path):
    """
    Return a GIF's first frame scaled to the tile, or None when unavailable.

    The QMovie is local so its file handle is released once the frame is copied.
    """
    if not gif_path or not Path(gif_path).exists():
        return None

    movie = QMovie(str(gif_path))
    movie.jumpToFrame(0)
    frame = movie.currentPixmap()
    if frame.isNull():
        return None

    return frame.scaled(_fit_size(frame.size()), Qt.KeepAspectRatio, Qt.SmoothTransformation)


class CollectionItemWidget(QWidget):
    """Widget representing a single shiny Pokemon in the collection"""

    def __init__(self, shiny, static_frame, collection, parent=None):
        """
        Args:
            shiny: Dict with name, rarity, count, and gif_path keys
            static_frame: Pre-rendered first frame QPixmap, or None when missing
            collection: Owning CollectionWindow, which drives hover animation
            parent: Parent widget
        """
        super().__init__(parent)
        self.pokemon_name = shiny['name']
        self.rarity = shiny['rarity']
        self.count = shiny['count']
        self.gif_path = shiny['gif_path']
        self.static_frame = static_frame
        self.collection = collection
        self.gif_label = None

        self.setup_ui()
        # Enable mouse tracking for hover events
        self.setMouseTracking(True)

    def setup_ui(self):
        """Setup the collection item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Container with dark background
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {UIColors.BG_DARKER};
                border: 2px solid {UIColors.BORDER_SHINY};
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(5)

        # Pokemon GIF, shown as a still frame until the item is hovered
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setFixedSize(GIF_SIZE, GIF_SIZE)
        self.gif_label.setStyleSheet("background: transparent; border: none;")

        if self.static_frame is not None:
            self.gif_label.setPixmap(self.static_frame)
        else:
            # Fallback if GIF not found
            self.gif_label.setText("?")
            self.gif_label.setStyleSheet(f"""
                background: transparent;
                border: none;
                color: {UIColors.TEXT_SHINY};
                font-size: 48px;
                font-weight: bold;
            """)

        container_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)

        # Pokemon name
        name_label = QLabel(self.pokemon_name)
        name_label.setStyleSheet(
            transparent_label_style(
                UIColors.TEXT_SHINY,
                font_size=13,
                bold=True,
                padding=0,
                extra="border: none;",
            )
        )
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        container_layout.addWidget(name_label)

        # Rarity
        rarity_label = QLabel(self.rarity)
        rarity_label.setStyleSheet(
            transparent_label_style(
                UIColors.TEXT_SECONDARY,
                font_size=10,
                padding=0,
                extra="border: none;",
            )
        )
        rarity_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(rarity_label)

        # Count badge
        if self.count > 1:
            count_label = QLabel(f"x{self.count}")
            count_label.setStyleSheet(f"""
                QLabel {{
                    color: {UIColors.TEXT_PRIMARY};
                    font-size: 11px;
                    font-weight: bold;
                    background-color: {UIColors.BADGE_BG};
                    border: none;
                    border-radius: 10px;
                    padding: 3px 8px;
                }}
            """)
            count_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(count_label, alignment=Qt.AlignCenter)

        layout.addWidget(container)
        self.setFixedSize(ITEM_WIDTH, ITEM_HEIGHT)

    def show_static_frame(self):
        """Return the tile to its non-animated first frame."""
        if self.static_frame is not None:
            self.gif_label.setPixmap(self.static_frame)

    def enterEvent(self, event):
        """Start GIF animation when mouse enters the widget"""
        self.collection.start_hover(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Stop GIF animation and return to first frame when mouse leaves"""
        self.collection.stop_hover(self)
        super().leaveEvent(event)


class CollectionWindow(QDialog):
    """Window displaying the shiny Pokemon collection"""

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.shiny_data = []
        self.filtered_data = []
        self.scroll_area = None  # Store reference for width calculation
        self.current_columns = 0

        # Still frames are cached so rebuilding the grid does not re-decode GIFs.
        self.static_frames = {}

        # One shared QMovie animates whichever tile is hovered. QLabel.setMovie()
        # retains every movie it is given, so a movie per tile would keep one file
        # handle open per collected shiny.
        self.hover_movie = QMovie(self)
        self.hover_movie.setSpeed(GIF_ANIMATION_SPEED)
        self.hovered_item = None

        self.setWindowTitle("Shiny Pokémon Collection")
        self.setModal(False)
        self.resize(700, 600)

        self.setup_ui()
        self.load_collection_data()

    def setup_ui(self):
        """Setup the collection window UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Set window background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {UIColors.BG_DARK};
            }}
        """)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        # Title
        title_label = QLabel("Shiny Pokémon Collection")
        title_label.setStyleSheet(
            transparent_label_style(UIColors.TEXT_SHINY, font_size=20, bold=True, padding=10)
        )
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Search and filter controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Pokémon...")
        self.search_bar.setStyleSheet(line_edit_style())
        self.search_bar.textChanged.connect(self.filter_collection)
        controls_layout.addWidget(self.search_bar, stretch=2)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort by Name", "Sort by Rarity", "Sort by Count"])
        self.sort_combo.setStyleSheet(combo_box_style())
        self.sort_combo.currentIndexChanged.connect(self.sort_collection)
        controls_layout.addWidget(self.sort_combo, stretch=1)

        header_layout.addLayout(controls_layout)
        main_layout.addLayout(header_layout)

        # Collection count label
        self.count_label = QLabel("Total Shinies: 0")
        self.count_label.setStyleSheet(transparent_label_style(font_size=12))
        main_layout.addWidget(self.count_label)

        # Scrollable collection area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {UIColors.SCROLLBAR_BG};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {UIColors.SCROLLBAR_HANDLE};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {UIColors.SCROLLBAR_HOVER};
            }}
        """)

        # Collection grid container
        self.collection_widget = QWidget()
        self.collection_layout = QGridLayout(self.collection_widget)
        self.collection_layout.setSpacing(GRID_SPACING)
        self.collection_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.collection_widget)
        main_layout.addWidget(self.scroll_area)

        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_SECONDARY,
                UIColors.PRIMARY_BLUE,
                pressed_color=UIColors.PRIMARY_BLUE,
                pressed_opacity=0.8,
                font_size=13,
                padding="10px 20px",
            )
        )
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def load_collection_data(self):
        """Load shiny collection data from save data."""
        all_shinies = self.data_manager.get_all_shinies()

        self.shiny_data = []
        for pokemon_name, data in all_shinies.items():
            gif_path = find_pokemon_gif(pokemon_name, is_shiny=True)

            self.shiny_data.append({
                'name': pokemon_name,
                'rarity': data['rarity'],
                'count': data['count'],
                'gif_path': str(gif_path) if gif_path else None
            })

        # Initial sort by name
        self.shiny_data.sort(key=lambda x: x['name'])
        self.filtered_data = self.shiny_data.copy()

        self.update_collection_display()

    def calculate_columns(self):
        """Calculate optimal number of columns based on available width"""
        if not self.scroll_area:
            return DEFAULT_COLUMNS

        # Get available width (accounting for scrollbar and margins)
        available_width = self.scroll_area.viewport().width() - SCROLL_MARGIN

        # Each item includes width + spacing
        total_item_width = ITEM_WIDTH + GRID_SPACING

        return max(MIN_COLUMNS, min(int(available_width / total_item_width), MAX_COLUMNS))

    def start_hover(self, item):
        """Animate a hovered tile using the shared movie."""
        if item.static_frame is None:
            return

        self.stop_hover()

        self.hover_movie.stop()
        # Clear previous scaling so the new GIF's native frame size can be read.
        self.hover_movie.setScaledSize(QSize())
        self.hover_movie.setFileName(item.gif_path)
        self.hover_movie.jumpToFrame(0)

        native_size = self.hover_movie.currentPixmap().size()
        if not native_size.isEmpty():
            self.hover_movie.setScaledSize(_fit_size(native_size))

        item.gif_label.setMovie(self.hover_movie)
        self.hover_movie.start()
        self.hovered_item = item

    def stop_hover(self, item=None):
        """
        Stop the shared animation and restore the still frame.

        Leave events can arrive after the next tile's enter event, so a leave from
        a tile that is no longer the hovered one is ignored.
        """
        if self.hovered_item is None or (item is not None and item is not self.hovered_item):
            return

        self.hover_movie.stop()
        self.hovered_item.gif_label.setMovie(None)
        self.hovered_item.show_static_frame()
        self.hovered_item = None

    def _static_frame(self, shiny):
        """Return the cached tile-sized first frame for a shiny."""
        name = shiny['name']
        if name not in self.static_frames:
            self.static_frames[name] = _load_first_frame(shiny['gif_path'])
        return self.static_frames[name]

    def update_collection_display(self):
        """Update the collection grid display"""
        # Tiles are about to be destroyed, so drop any hover state pointing at them.
        self.stop_hover()

        # Clear existing items
        while self.collection_layout.count():
            item = self.collection_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Update count label
        total_count = sum(item['count'] for item in self.filtered_data)
        unique_count = len(self.filtered_data)
        self.count_label.setText(f"Total Shinies: {total_count} ({unique_count} unique)")

        # Display empty state if no shinies
        if not self.filtered_data:
            self.current_columns = 0
            empty_label = QLabel("No shiny Pokémon found yet.\nKeep hunting!" if not self.shiny_data
                                 else "No matching Pokémon found.")
            empty_label.setStyleSheet(
                transparent_label_style(
                    UIColors.TEXT_SECONDARY,
                    font_size=16,
                    padding=50,
                    extra="font-style: italic;",
                )
            )
            empty_label.setAlignment(Qt.AlignCenter)
            self.collection_layout.addWidget(empty_label, 0, 0, 1, 3)
            return

        # Add collection items to grid with dynamic columns
        self.current_columns = self.calculate_columns()
        for index, shiny in enumerate(self.filtered_data):
            item_widget = CollectionItemWidget(shiny, self._static_frame(shiny), self)
            self.collection_layout.addWidget(
                item_widget,
                index // self.current_columns,
                index % self.current_columns,
                alignment=Qt.AlignCenter,
            )

    def filter_collection(self):
        """Filter collection based on search text"""
        search_text = self.search_bar.text().lower()

        if not search_text:
            self.filtered_data = self.shiny_data.copy()
        else:
            self.filtered_data = [
                item for item in self.shiny_data
                if search_text in item['name'].lower()
            ]

        self.update_collection_display()

    def sort_collection(self):
        """Sort collection based on selected criteria"""
        sort_index = self.sort_combo.currentIndex()

        if sort_index == 0:  # Sort by Name
            self.shiny_data.sort(key=lambda x: x['name'])
        elif sort_index == 1:  # Sort by Rarity
            self.shiny_data.sort(key=lambda x: RARITY_ORDER.get(x['rarity'], 99))
        elif sort_index == 2:  # Sort by Count
            self.shiny_data.sort(key=lambda x: x['count'], reverse=True)

        # Reapply filter after sorting
        self.filter_collection()

    def resizeEvent(self, event):
        """Rebuild the grid only when the column count actually changes"""
        super().resizeEvent(event)
        if self.filtered_data and self.calculate_columns() != self.current_columns:
            self.update_collection_display()
