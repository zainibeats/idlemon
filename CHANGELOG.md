# Changelog

## [0.3.0] - Unreleased

### Changed

- Simplified startup config validation to require file presence instead of strict hardcoded hashes.
- Switched Windows packaging to an explicit portable one-folder PyInstaller build.
- Updated the README and development docs to match the actual Windows and Linux release strategy.

### Fixed

- Fixed first-run startup when `logs/shiny_count.bin` does not exist.
- Preserved advanced config values when saving settings from the UI.
- Normalized Windows-style config paths so Linux source runs do not need manual path edits.
