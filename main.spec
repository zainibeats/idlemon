# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


SPEC_PATH = Path(SPEC).resolve()
PROJECT_ROOT = SPEC_PATH.parent

# Collect all PySide6 data, binaries, and hidden imports.
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all("PySide6")

added_files = [
    ("assets", "assets"),
    ("config", "config"),
    ("README.md", "."),
    ("LICENSE", "."),
]

a = Analysis(
    ["src/main.py"],
    pathex=[str(PROJECT_ROOT), str(PROJECT_ROOT / "src")],
    binaries=pyside6_binaries,
    datas=added_files + pyside6_datas,
    hiddenimports=pyside6_hiddenimports + [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtMultimedia",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pygame"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IdleMon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "assets/images/icon.ico") if (PROJECT_ROOT / "assets/images/icon.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="IdleMon",
)
