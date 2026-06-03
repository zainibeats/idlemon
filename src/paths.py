"""Central path helpers for portable source and packaged builds."""
import sys
from pathlib import Path


CONFIG_DIR_NAME = "config"
CONFIG_FILE_NAME = "config.json"


def get_base_path():
    """Return the source root or PyInstaller executable directory."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


PROJECT_ROOT = get_base_path()


def get_config_dir():
    """Return the portable writable config directory."""
    return PROJECT_ROOT / CONFIG_DIR_NAME


def get_config_file():
    """Return the primary persisted settings file."""
    return get_config_dir() / CONFIG_FILE_NAME


def get_legacy_config_file():
    """Return the pre-portable root config path."""
    return PROJECT_ROOT / CONFIG_FILE_NAME


def get_logs_dir():
    """Return the portable writable logs directory."""
    return get_config_dir() / "logs"


def asset_path(*parts, root=None):
    """Return a path under the bundled assets directory."""
    base_path = PROJECT_ROOT if root is None else Path(root)
    return base_path / "assets" / Path(*parts)


def normalize_path_value(value):
    """Normalize config path strings so Windows-style paths still parse on Linux."""
    if isinstance(value, str):
        return value.replace("\\", "/")
    return value


def resolve_asset_path(path_value):
    """Resolve a configured asset path from the portable app root."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def resolve_config_path(path_value):
    """Resolve mutable runtime paths from the portable config directory."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return get_config_dir() / path


def resolve_background_path(path_value):
    """Resolve a configured background image with the default asset fallback."""
    background_path = resolve_asset_path(path_value)
    if background_path.exists():
        return background_path
    return asset_path("images", "default_background.jpg")
