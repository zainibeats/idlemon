"""Settings dialog for IdleMon configuration"""
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QFileDialog, QLineEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal
import paths
from ui_colors import UIColors
from ui_styles import button_style, group_box_style

# User-facing settings that only take effect after a restart.
RESTART_REQUIRED_SETTINGS = (
    ("borderless_mode", "Borderless mode"),
    ("background_image", "Background image"),
)


class SettingsDialog(QDialog):
    """Dialog for managing application settings"""

    settings_changed = Signal(dict)  # Emits new config when saved

    def __init__(self, current_config, parent=None):
        """
        Initialize settings dialog

        Args:
            current_config: Current configuration dict
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_config = current_config
        self.config_file_path = paths.get_config_file()
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
        save_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_PRIMARY,
                UIColors.ACCENT_HOVER,
                min_width=80,
            )
        )
        save_button.clicked.connect(self._save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_CANCEL,
                UIColors.BORDER_DEFAULT,
                min_width=80,
            )
        )
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def _create_display_group(self):
        """Create display settings group"""
        group = QGroupBox("Display & Audio Settings")
        group.setStyleSheet(group_box_style(UIColors.GROUP_DISPLAY))
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
        group.setStyleSheet(group_box_style(UIColors.GROUP_VISUAL))
        layout = QVBoxLayout()

        # Background Image
        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Image:")
        bg_label.setToolTip("Image displayed behind the Pokemon (normal mode only)")
        self.inputs['background_image'] = QLineEdit()
        self.inputs['background_image'].setToolTip("Enter a relative or absolute image path")

        browse_button = QPushButton("Browse...")
        browse_button.setStyleSheet(
            button_style(
                UIColors.BUTTON_SECONDARY,
                UIColors.PRIMARY_BLUE,
                border_radius=3,
                padding="5px 15px",
                bold=False,
            )
        )
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
            bg_path_obj = Path(bg_path)
            if bg_path_obj.is_absolute():
                try:
                    bg_path = str(bg_path_obj.relative_to(paths.PROJECT_ROOT))
                except ValueError:
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
            file_path_obj = Path(file_path)
            try:
                relative_path = str(file_path_obj.relative_to(paths.PROJECT_ROOT))
                self.inputs['background_image'].setText(relative_path)
            except ValueError:
                self.inputs['background_image'].setText(file_path)

    def _save_settings(self):
        """Save settings to the portable config file."""
        # Collect new settings (only user-configurable ones)
        updated_settings = {
            'borderless_mode': self.inputs['borderless_mode'].isChecked(),
            'mute_audio': self.inputs['mute_audio'].isChecked(),
            'background_image': self.inputs['background_image'].text()
        }
        new_config = {**self.current_config, **updated_settings}

        changed_restart_settings = [
            label for key, label in RESTART_REQUIRED_SETTINGS
            if updated_settings[key] != self.current_config.get(key)
        ]

        # Save only user-facing settings to the portable config file.
        try:
            self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_file_path.write_text(
                json.dumps(updated_settings, indent=4) + "\n",
                encoding="utf-8",
            )

            # Show restart message if needed
            if changed_restart_settings:
                changed_list = "\n".join(f" - {label}" for label in changed_restart_settings)
                QMessageBox.information(
                    self,
                    "Restart Required",
                    "These settings changed:\n"
                    f"{changed_list}\n\n"
                    "Please restart IdleMon for them to take effect."
                )

            # Emit signal with new config
            self.settings_changed.emit(new_config)
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"Failed to save settings to {self.config_file_path}:\n{str(e)}"
            )
