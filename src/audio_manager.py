"""Audio management module for sound effects"""
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from logger import logger


class AudioManager:
    """Manages game sound effects"""

    def __init__(self, project_root, mute_audio=False):
        """
        Initialize audio manager

        Args:
            project_root: Base path for assets
            mute_audio: Whether audio is muted
        """
        self.project_root = Path(project_root)
        self.mute_audio = mute_audio
        self.shiny_sound = None
        self.continue_sound = None

        if not mute_audio:
            self._load_sounds()

    def _load_sounds(self):
        """Load sound effects from assets"""
        # Load shiny sound
        shiny_sound_path = self.project_root / "assets" / "sounds" / "shiny_sound1.wav"
        if shiny_sound_path.exists():
            self.shiny_sound = QSoundEffect()
            self.shiny_sound.setSource(QUrl.fromLocalFile(str(shiny_sound_path)))
            self.shiny_sound.setVolume(1.0)
        else:
            logger.log_error(f"Shiny sound file not found: {shiny_sound_path}")

        # Load continue sound
        continue_sound_path = self.project_root / "assets" / "sounds" / "continue_sound1.wav"
        if continue_sound_path.exists():
            self.continue_sound = QSoundEffect()
            self.continue_sound.setSource(QUrl.fromLocalFile(str(continue_sound_path)))
            self.continue_sound.setVolume(1.0)
        else:
            logger.log_error(f"Continue sound file not found: {continue_sound_path}")

    def play_shiny_sound(self):
        """Play shiny encounter sound"""
        if self.shiny_sound and not self.mute_audio:
            self.shiny_sound.play()

    def play_continue_sound(self):
        """Play continue button sound"""
        if self.continue_sound and not self.mute_audio:
            self.continue_sound.play()
