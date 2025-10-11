"""Settings dialog for IdleMon configuration"""
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QDoubleSpinBox, QSpinBox, QFileDialog, QLineEdit,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from ui_colors import UIColors


class SettingsDialog(QDialog):
    """Dialog for managing application settings"""

    settings_changed = Signal(dict)  # Emits new config when saved

    def __init__(self, current_config, config_file_path, parent=None):
        """
        Initialize settings dialog

        Args:
            current_config: Current configuration dict
            config_file_path: Path to config.json file
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_config = current_config
        self.config_file_path = Path(config_file_path)
        self.setWindowTitle("IdleMon Settings")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Store references to input widgets
        self.inputs = {}

        self._setup_ui()
        self._load_current_values()

    def _setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Audio & Display Settings Group
        display_group = self._create_display_group()
        layout.addWidget(display_group)

        # Visual Settings Group
        visual_group = self._create_visual_group()
        layout.addWidget(visual_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIColors.BUTTON_PRIMARY};
                color: {UIColors.TEXT_PRIMARY};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {UIColors.ACCENT_HOVER};
            }}
        """)
        save_button.clicked.connect(self._save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIColors.BUTTON_CANCEL};
                color: {UIColors.TEXT_PRIMARY};
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {UIColors.BORDER_DEFAULT};
            }}
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)



    def _create_display_group(self):
        """Create display settings group"""
        group = QGroupBox("Display & Audio Settings")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {UIColors.TEXT_PRIMARY};
                border: 2px solid {UIColors.GROUP_DISPLAY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        layout = QVBoxLayout()

        # Borderless Mode
        self.inputs['borderless_mode'] = QCheckBox("Borderless Desktop Pet Mode")
        self.inputs['borderless_mode'].setToolTip("Transparent window with only Pokemon (requires restart)")
        layout.addWidget(self.inputs['borderless_mode'])

        # Mute Audio
        self.inputs['mute_audio'] = QCheckBox("Mute Audio")
        self.inputs['mute_audio'].setToolTip("Disable all sound effects")
        layout.addWidget(self.inputs['mute_audio'])

        group.setLayout(layout)
        return group

    def _create_visual_group(self):
        """Create visual settings group"""
        group = QGroupBox("Visual Settings")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {UIColors.TEXT_PRIMARY};
                border: 2px solid {UIColors.GROUP_VISUAL};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        layout = QVBoxLayout()

        # Background Image
        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Image:")
        bg_label.setToolTip("Image displayed behind the Pokemon (normal mode only)")
        self.inputs['background_image'] = QLineEdit()
        self.inputs['background_image'].setReadOnly(True)

        browse_button = QPushButton("Browse...")
        browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIColors.BUTTON_SECONDARY};
                color: {UIColors.TEXT_PRIMARY};
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {UIColors.PRIMARY_BLUE};
            }}
        """)
        browse_button.clicked.connect(self._browse_background)

        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.inputs['background_image'])
        bg_layout.addWidget(browse_button)
        layout.addLayout(bg_layout)

        group.setLayout(layout)
        return group

    def _load_current_values(self):
        """Load current configuration values into input fields"""
        self.inputs['borderless_mode'].setChecked(self.current_config.get('borderless_mode', False))
        self.inputs['mute_audio'].setChecked(self.current_config.get('mute_audio', False))

        # Get relative path for display if possible
        bg_path = self.current_config.get('background_image', '')
        if bg_path:
            try:
                # Try to make it relative to project root for cleaner display
                from config_loader import PROJECT_ROOT
                bg_path_obj = Path(bg_path)
                if bg_path_obj.is_absolute():
                    try:
                        bg_path = str(bg_path_obj.relative_to(PROJECT_ROOT))
                    except ValueError:
                        # Can't make relative, use absolute
                        pass
            except:
                pass
        self.inputs['background_image'].setText(bg_path)

    def _browse_background(self):
        """Open file browser for background image selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            # Try to make path relative to project root
            try:
                from config_loader import PROJECT_ROOT
                file_path_obj = Path(file_path)
                try:
                    relative_path = str(file_path_obj.relative_to(PROJECT_ROOT))
                    self.inputs['background_image'].setText(relative_path)
                except ValueError:
                    # Can't make relative, use absolute
                    self.inputs['background_image'].setText(file_path)
            except:
                self.inputs['background_image'].setText(file_path)

    def _save_settings(self):
        """Save settings to config.json"""
        # Collect new settings (only user-configurable ones)
        new_config = {
            'borderless_mode': self.inputs['borderless_mode'].isChecked(),
            'mute_audio': self.inputs['mute_audio'].isChecked(),
            'background_image': self.inputs['background_image'].text()
        }

        # Check if borderless mode changed
        borderless_changed = (
            new_config['borderless_mode'] != self.current_config.get('borderless_mode', False)
        )

        # Save to config.json
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(new_config, f, indent=4)

            # Show restart message if needed
            if borderless_changed:
                QMessageBox.information(
                    self,
                    "Restart Required",
                    "Borderless mode setting has changed.\nPlease restart IdleMon for changes to take effect."
                )

            # Emit signal with new config
            self.settings_changed.emit(new_config)
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"Failed to save settings to config.json:\n{str(e)}"
            )
