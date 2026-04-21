# IdleMon Release Checklist

## Code

- Confirm the app starts from source without strict data hash validation.
- Confirm first-run persistence works when `logs/` is missing.
- Confirm settings saves do not discard advanced config keys.

## Versioning

- Update `VERSION`.
- Update `src/version.py`.
- Update `CHANGELOG.md`.

## Windows

- Build with `pyinstaller --clean main.spec`.
- Verify `dist/IdleMon/IdleMon.exe` exists.
- Verify `dist/IdleMon/assets/` exists.
- Verify `dist/IdleMon/config.json` exists.
- Zip the folder as the release artifact.

## Linux

- Keep Linux support documented as source-run only unless release scope changes.
- Verify `docs/linux-setup.md` still matches the current dependency and run path.

## Documentation

- Ensure `README.md`, `docs/development.md`, `docs/windows-portable-build.md`, and `docs/linux-setup.md` agree on release format and run instructions.
- Ensure `docs/release-process.md` and the current versioned release notes are updated.
