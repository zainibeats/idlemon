---
name: idlemon-release
description: Prepare and document IdleMon releases on the dev branch. Use when Codex needs to update the changelog, align packaging with the current runtime model, build or document the Windows portable one-folder zip, document Linux source-run support, or verify release-readiness without drifting into other branches.
---

# IdleMon Release

Use this skill to handle repeatable release work for IdleMon with minimal churn.

## Workflow

1. Read `README.md`, `CHANGELOG.md`, `docs/development.md`, `docs/release-process.md`, `docs/windows-portable-build.md`, and `docs/linux-setup.md`.
2. Confirm the current version from `VERSION` and `src/version.py`.
3. Keep release work scoped to the current branch unless the user explicitly says otherwise.
4. Prefer small fixes that keep the codebase simple over adding new abstractions.
5. When packaging changes are involved, verify that runtime path handling in `src/config_loader.py` still matches the documented release format.

## Windows Packaging

- Treat Windows as a portable one-folder release.
- Use `main.spec` as the source of truth for packaging.
- Ensure the packaged app keeps `IdleMon.exe`, `config.json`, and `assets/` in the same folder tree.
- If the packaging layout changes, update both `README.md` and `docs/windows-portable-build.md` in the same change.

## Linux Support

- Treat Linux as source-run only unless the user explicitly requests binary packaging.
- Keep Linux instructions in `docs/linux-setup.md`.
- Prefer documenting distro package prerequisites and the `python src/main.py` path over speculative packaging steps.

## Changelog And Docs

- Keep `CHANGELOG.md` concise and user-facing.
- Keep `docs/development.md` focused on contributors.
- Keep `docs/release-process.md` and versioned release notes aligned with the actual release artifact.
- Keep `README.md` short and aligned with the actual release artifacts.

## References

- Read `references/release-checklist.md` before cutting or documenting a release.
