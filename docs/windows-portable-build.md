# Build the Windows Portable Release

IdleMon `0.3.0` ships on Windows as a portable one-folder build that is zipped for distribution.

## Build Environment

- Windows
- Python 3.9 or later
- A fresh virtual environment is recommended

Install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Build

Run from the repository root:

```powershell
pyinstaller --clean main.spec
```

This creates a portable folder at:

```text
dist\IdleMon\
```

Expected contents include:

- `IdleMon.exe`
- `assets\`
- `config.json`
- bundled Qt and Python runtime files

## Smoke Check

Before zipping:

1. Open `dist\IdleMon\`.
2. Run `IdleMon.exe`.
3. Confirm the main window opens.
4. Confirm `logs\` is created after startup.
5. Confirm GIFs load and audio works when enabled.

## Create Release Zip

From the repository root in PowerShell:

```powershell
Compress-Archive -Path dist\IdleMon\* -DestinationPath dist\IdleMon-0.3.0-windows-portable.zip -Force
```

## Release Notes Checklist

- Update [../CHANGELOG.md](../CHANGELOG.md) if release notes changed.
- Verify `config.json` is present in the portable folder.
- Verify `assets\data\` and `assets\gifs\` were bundled.
- Verify the zip extracts into a single `IdleMon` folder layout for users.

## Why One-Folder

IdleMon resolves runtime assets relative to the executable folder in packaged mode. A portable one-folder build keeps the executable, config, and assets together and matches the app's runtime path model.
