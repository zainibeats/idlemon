# Release Process

This is the current release process for IdleMon `0.3.x` on the `dev` branch.

## Scope

- Windows release artifact: portable one-folder zip
- Linux release artifact: none
- Linux support: run from source only

## Pre-Release Checks

1. Update `VERSION`.
2. Update `src/version.py`.
3. Update `CHANGELOG.md`.
4. Review `README.md`, `docs/development.md`, `docs/windows-portable-build.md`, and `docs/linux-setup.md` for drift.
5. Run:

```bash
python -m compileall src
```

## Windows Build

Follow [windows-portable-build.md](windows-portable-build.md).

Build command:

```powershell
pyinstaller --clean main.spec
```

Expected output:

```text
dist\IdleMon\
```

## Manual Smoke Test

On Windows:

1. Launch `dist\IdleMon\IdleMon.exe`.
2. Confirm the main window opens.
3. Confirm `logs\` is created automatically.
4. Confirm GIFs animate.
5. Confirm audio plays when not muted.
6. Confirm the settings dialog saves changes.
7. Confirm the collection window opens.

## Package Release Artifact

Zip the portable folder:

```powershell
Compress-Archive -Path dist\IdleMon\* -DestinationPath dist\IdleMon-0.3.0-windows-portable.zip -Force
```

## Publish

1. Create the `0.3.0` release/tag.
2. Attach `IdleMon-0.3.0-windows-portable.zip`.
3. Use [release-notes-0.3.0.md](release-notes-0.3.0.md) as the starting release notes.
