# IdleMon

IdleMon is a small PySide6 desktop app that simulates Pokemon encounters and shiny hunting. It runs from source on Linux and is packaged as a portable one-folder Windows build.

![screenshot of shiny Giratina encounter](https://assets.czaini.net/images/giratina-screenshot.jpg)

## Release Status

- Current development version: `0.3.0`
- Windows release format: portable one-folder zip
- Linux release format: source-run only for now

## Features

- Animated normal and shiny encounter GIFs across generations 1-5
- Shiny counter, encounter counter, and elapsed timer
- Searchable shiny collection with sorting and duplicate counts
- Optional borderless desktop pet mode
- Local portable settings, save data, and logs in `config/`
- Configurable audio and background image

## Quick Start

### Windows

1. Download the latest Windows release zip.
2. Extract it.
3. Run `IdleMon.exe` from the extracted `IdleMon/` folder.

### Linux

Follow [docs/linux-setup.md](docs/linux-setup.md) to install dependencies and run from source.

## Development

Use [docs/development.md](docs/development.md) for local development and project structure.

## Configuration

IdleMon stores settings in `config/config.json` beside the executable or project root. This keeps the Windows build portable: the extracted `IdleMon/` folder contains both the app and its writable user data.

Supported user-facing settings:

- `borderless_mode`
- `mute_audio`
- `background_image`

Example:

```json
{
  "borderless_mode": false,
  "mute_audio": false,
  "background_image": "assets/images/default_background.jpg"
}
```

## Save Data

IdleMon stores runtime data in `config/`:

- `save_data.json`: shiny count and shiny collection history
- `logs/error.log`: runtime errors

Delete `config/save_data.json` to reset progress.

## Troubleshooting

- If the app does not start, confirm `assets/` exists beside `IdleMon.exe` in the Windows build.
- Keep the extracted Windows folder in a writable location so IdleMon can update `config/`.
- If GIFs or sounds are missing, rebuild the portable folder and verify the `assets/` directory was included.
- If Linux shows Qt plugin errors, follow the dependency notes in [docs/linux-setup.md](docs/linux-setup.md).

## License

This project is licensed under the MIT License.
