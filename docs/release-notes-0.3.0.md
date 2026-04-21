# IdleMon 0.3.0

IdleMon `0.3.0` focuses on release readiness, simpler startup behavior, and a cleaner packaging story.

## Highlights

- Windows now targets a portable one-folder release layout.
- Linux support is documented directly in this branch as source-run only.
- Startup no longer depends on brittle hardcoded hashes for Pokemon data files.
- First-run save creation is fixed.
- Settings saves no longer discard advanced config values.

## Release Details

### Windows

- Release artifact: `IdleMon-0.3.0-windows-portable.zip`
- Extract the zip and run `IdleMon.exe` from the `IdleMon/` folder.

### Linux

- There is no Linux binary release for `0.3.0`.
- Run from source using [linux-setup.md](linux-setup.md).

## Internal Changes

- Added explicit version files for the release.
- Reworked release documentation to match the actual runtime and packaging model.
- Added a repo-committed release skill for future release work.
