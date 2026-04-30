# IdleMon

IdleMon is a small PySide6 desktop app that simulates Pokemon encounters and shiny hunting. It runs from source on Linux and is packaged as a portable one-folder Windows build.

![screenshot of shiny Giratina encounter](assets/images/giratina-screenshot.png)

## Release Status

- Current development version: `0.3.0`
- Windows release format: portable one-folder zip
- Linux release format: source-run only for now

## Features

- Animated normal and shiny encounter GIFs across generations 1-5
- Shiny counter, encounter counter, and elapsed timer
- Searchable shiny collection with sorting and duplicate counts
- Optional borderless desktop pet mode
- Local portable save data in `logs/`
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

IdleMon stores settings in `config.json` beside the executable or project root.

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

IdleMon stores runtime data in `logs/`:

- `shiny_count.bin`: total shiny count
- `shinies_encountered.txt`: shiny collection history
- `error.log`: runtime errors

Delete `logs/` to reset progress.

## Troubleshooting

- If the app does not start, confirm `assets/` exists beside `IdleMon.exe` in the Windows build.
- If GIFs or sounds are missing, rebuild the portable folder and verify the `assets/` directory was included.
- If Linux shows Qt plugin errors, follow the dependency notes in [docs/linux-setup.md](docs/linux-setup.md).

## License

This project is licensed under the MIT License.
