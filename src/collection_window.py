"""Collection window module for displaying shiny Pokemon collection"""
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QWidget, QGridLayout, QLineEdit, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie, QPixmap
from ui_colors import UIColors


class CollectionItemWidget(QWidget):
    """Widget representing a single shiny Pokemon in the collection"""

    def __init__(self, pokemon_name, rarity, count, gif_path, parent=None):
        super().__init__(parent)
        self.pokemon_name = pokemon_name
        self.rarity = rarity
        self.count = count
        self.gif_path = gif_path
        self.movie = None  # Store movie reference for hover control

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

        # Pokemon GIF
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setFixedSize(120, 120)
        self.gif_label.setStyleSheet("background: transparent; border: none;")

        # Load GIF but don't animate until hover
        if self.gif_path and Path(self.gif_path).exists():
            self.movie = QMovie(str(self.gif_path))
            # Scale the movie to fit nicely
            original_size = self.movie.scaledSize()
            if original_size.width() > 0 and original_size.height() > 0:
                scale_factor = min(100 / original_size.width(), 100 / original_size.height())
                new_size = QSize(
                    int(original_size.width() * scale_factor),
                    int(original_size.height() * scale_factor)
                )
                self.movie.setScaledSize(new_size)
            self.movie.setSpeed(100)

            # Show first frame as static image (don't animate until hover)
            self.movie.jumpToFrame(0)
            first_frame = self.movie.currentPixmap()
            self.gif_label.setPixmap(first_frame)
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
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {UIColors.TEXT_SHINY};
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        container_layout.addWidget(name_label)

        # Rarity
        rarity_label = QLabel(self.rarity)
        rarity_label.setStyleSheet(f"""
            QLabel {{
                color: {UIColors.TEXT_SECONDARY};
                font-size: 10px;
                background: transparent;
                border: none;
            }}
        """)
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
        self.setFixedSize(150, 220)

    def enterEvent(self, event):
        """Start GIF animation when mouse enters the widget"""
        if self.movie:
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Stop GIF animation and return to first frame when mouse leaves"""
        if self.movie:
            self.movie.stop()
            self.movie.jumpToFrame(0)
            first_frame = self.movie.currentPixmap()
            self.gif_label.setPixmap(first_frame)
        super().leaveEvent(event)


class CollectionWindow(QDialog):
    """Window displaying the shiny Pokemon collection"""

    def __init__(self, logger, project_root, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.project_root = Path(project_root)
        self.shiny_data = []
        self.filtered_data = []
        self.scroll_area = None  # Store reference for width calculation

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
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {UIColors.TEXT_SHINY};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Search and filter controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Pokémon...")
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {UIColors.BG_LIGHT};
                color: {UIColors.TEXT_DARK};
                border: 2px solid {UIColors.BORDER_DEFAULT};
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {UIColors.BORDER_FOCUS};
            }}
        """)
        self.search_bar.textChanged.connect(self.filter_collection)
        controls_layout.addWidget(self.search_bar, stretch=2)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort by Name", "Sort by Rarity", "Sort by Count"])
        self.sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {UIColors.BG_LIGHT};
                color: {UIColors.TEXT_DARK};
                border: 2px solid {UIColors.BORDER_DEFAULT};
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {UIColors.BG_LIGHT};
                color: {UIColors.TEXT_DARK};
                selection-background-color: {UIColors.BUTTON_SECONDARY};
                selection-color: {UIColors.TEXT_PRIMARY};
            }}
        """)
        self.sort_combo.currentIndexChanged.connect(self.sort_collection)
        controls_layout.addWidget(self.sort_combo, stretch=1)

        header_layout.addLayout(controls_layout)
        main_layout.addLayout(header_layout)

        # Collection count label
        self.count_label = QLabel("Total Shinies: 0")
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {UIColors.TEXT_PRIMARY};
                font-size: 12px;
                padding: 5px;
            }}
        """)
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
        self.collection_layout.setSpacing(15)
        self.collection_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.collection_widget)
        main_layout.addWidget(self.scroll_area)

        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIColors.BUTTON_SECONDARY};
                color: {UIColors.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {UIColors.PRIMARY_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.PRIMARY_BLUE};
                opacity: 0.8;
            }}
        """)
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def load_collection_data(self):
        """Load shiny collection data from logger"""
        all_shinies = self.logger.get_all_shinies()

        self.shiny_data = []
        for pokemon_name, data in all_shinies.items():
            # Find the GIF path
            gif_path = self.find_shiny_gif(pokemon_name)

            self.shiny_data.append({
                'name': pokemon_name,
                'rarity': data['rarity'],
                'count': data['count'],
                'gif_path': gif_path
            })

        # Initial sort by name
        self.shiny_data.sort(key=lambda x: x['name'])
        self.filtered_data = self.shiny_data.copy()

        self.update_collection_display()

    def find_shiny_gif(self, pokemon_name):
        """Find the shiny GIF path for a Pokemon"""
        for gen in range(1, 6):
            gif_path = self.project_root / "assets" / "gifs" / f"gen{gen}" / "shiny" / f"{pokemon_name}.gif"
            if gif_path.exists():
                return str(gif_path)
        return None

    def calculate_columns(self):
        """Calculate optimal number of columns based on available width"""
        if not self.scroll_area:
            return 4  # Default fallback

        # Get available width (accounting for scrollbar and margins)
        available_width = self.scroll_area.viewport().width() - 20  # Subtract margins

        # Each item is 150px wide + 15px spacing
        item_width = 150
        spacing = 15
        total_item_width = item_width + spacing

        # Calculate how many fit, minimum 1, maximum reasonable is around 8
        columns = max(1, min(int(available_width / (item_width + spacing)), 8))

        # Fallback to 4 columns if calculation fails
        if columns < 1:
            columns = 4

        return columns

    def update_collection_display(self):
        """Update the collection grid display"""
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
            empty_label = QLabel("No shiny Pokémon found yet.\nKeep hunting!" if not self.shiny_data
                                 else "No matching Pokémon found.")
            empty_label.setStyleSheet(f"""
                QLabel {{
                    color: {UIColors.TEXT_SECONDARY};
                    font-size: 16px;
                    font-style: italic;
                    padding: 50px;
                }}
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            self.collection_layout.addWidget(empty_label, 0, 0, 1, 3)
            return

        # Add collection items to grid with dynamic columns
        columns = self.calculate_columns()
        for index, shiny in enumerate(self.filtered_data):
            row = index // columns
            col = index % columns

            item_widget = CollectionItemWidget(
                shiny['name'],
                shiny['rarity'],
                shiny['count'],
                shiny['gif_path']
            )
            self.collection_layout.addWidget(item_widget, row, col, alignment=Qt.AlignCenter)

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
            rarity_order = {
                'Very Rare': 0,
                'Rare': 1,
                'Semi-rare': 2,
                'Common': 3,
                'Very Common': 4
            }
            self.shiny_data.sort(key=lambda x: rarity_order.get(x['rarity'], 99))
        elif sort_index == 2:  # Sort by Count
            self.shiny_data.sort(key=lambda x: x['count'], reverse=True)

        # Reapply filter after sorting
        self.filter_collection()

    def resizeEvent(self, event):
        """Handle window resize to recalculate grid layout"""
        super().resizeEvent(event)
        # Only update if we have data to display
        if self.filtered_data:
            self.update_collection_display()
