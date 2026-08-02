"""Audio management module for sound effects"""
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
import paths

SHINY_SOUND_FILE = "shiny_sound1.wav"
CONTINUE_SOUND_FILE = "continue_sound1.wav"


class AudioManager:
    """Manages game sound effects"""

    def __init__(self, mute_audio, logger):
        """
        Initialize audio manager

        Args:
            mute_audio: Whether audio is muted
            logger: LogManager instance
        """
        self.mute_audio = mute_audio
        self.logger = logger
        self.shiny_sound = None
        self.continue_sound = None

        if not mute_audio:
            self._load_sounds()

    def _load_sound(self, file_name):
        """Load a single sound effect, or return None when the asset is missing."""
        sound_path = paths.asset_path("sounds", file_name)
        if not sound_path.exists():
            self.logger.log_error(f"Sound file not found: {sound_path}")
            return None

        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(str(sound_path)))
        effect.setVolume(1.0)
        return effect

    def _load_sounds(self):
        """Load any sound effects that are not loaded yet."""
        if self.shiny_sound is None:
            self.shiny_sound = self._load_sound(SHINY_SOUND_FILE)
        if self.continue_sound is None:
            self.continue_sound = self._load_sound(CONTINUE_SOUND_FILE)

    def play_shiny_sound(self):
        """Play shiny encounter sound"""
        if self.shiny_sound and not self.mute_audio:
            self.shiny_sound.play()

    def play_continue_sound(self):
        """Play continue button sound"""
        if self.continue_sound and not self.mute_audio:
            self.continue_sound.play()

    def set_mute(self, mute):
        """
        Set audio mute state

        Args:
            mute: Boolean indicating whether to mute audio
        """
        self.mute_audio = mute
        if not mute:
            self._load_sounds()
