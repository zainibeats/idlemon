# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Get the project root directory
PROJECT_ROOT = Path(os.getcwd())

# Collect all PySide6 data, binaries, and hidden imports
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')

added_files = [
    ('assets/sounds/*.wav', 'assets/sounds'),
    ('assets/images/*.jpg', 'assets/images'),
    ('assets/images/*.ico', 'assets/images'),
    ('assets/images/*.png', 'assets/images'),
    ('assets/gifs/gen1/normal/*', 'assets/gifs/gen1/normal'),
    ('assets/gifs/gen1/shiny/*', 'assets/gifs/gen1/shiny'),
    ('assets/gifs/gen2/normal/*', 'assets/gifs/gen2/normal'),
    ('assets/gifs/gen2/shiny/*', 'assets/gifs/gen2/shiny'),
    ('assets/gifs/gen3/normal/*', 'assets/gifs/gen3/normal'),
    ('assets/gifs/gen3/shiny/*', 'assets/gifs/gen3/shiny'),
    ('assets/gifs/gen4/normal/*', 'assets/gifs/gen4/normal'),
    ('assets/gifs/gen4/shiny/*', 'assets/gifs/gen4/shiny'),
    ('assets/gifs/gen5/normal/*', 'assets/gifs/gen5/normal'),
    ('assets/gifs/gen5/shiny/*', 'assets/gifs/gen5/shiny'),
    ('assets/data/*', 'assets/data'),
    ('config.json', '.'),
]

# Add PySide6 platform plugins explicitly for reliability
# This ensures Qt can initialize properly on the target system
try:
    import PySide6
    pyside6_path = os.path.dirname(PySide6.__file__)
    qt_plugins_path = os.path.join(pyside6_path, 'Qt', 'plugins')

    # Add platform plugins (required for Qt to start)
    platforms_path = os.path.join(qt_plugins_path, 'platforms')
    if os.path.exists(platforms_path):
        added_files.append((platforms_path, 'PySide6/Qt/plugins/platforms'))
        print(f"[+] Added Qt platform plugins from: {platforms_path}")

    # Add style plugins (for proper UI rendering)
    styles_path = os.path.join(qt_plugins_path, 'styles')
    if os.path.exists(styles_path):
        added_files.append((styles_path, 'PySide6/Qt/plugins/styles'))
        print(f"[+] Added Qt style plugins from: {styles_path}")

    # Add multimedia plugins (for QSoundEffect)
    multimedia_path = os.path.join(qt_plugins_path, 'multimedia')
    if os.path.exists(multimedia_path):
        added_files.append((multimedia_path, 'PySide6/Qt/plugins/multimedia'))
        print(f"[+] Added Qt multimedia plugins from: {multimedia_path}")
except ImportError:
    print("[!] Warning: PySide6 not found, Qt plugins will not be explicitly added")
except Exception as e:
    print(f"[!] Warning: Error finding Qt plugins: {e}")

a = Analysis(
    ['src/main.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=pyside6_binaries,
    datas=added_files + pyside6_datas,
    hiddenimports=pyside6_hiddenimports + [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtMultimedia',
        # Additional modules that might be needed
        'PySide6.QtNetwork',  # Sometimes required for Qt internals
        'PySide6.QtSvg',      # For SVG support if used
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pygame'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IdleMon',
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
    icon='assets/images/icon.ico' if os.path.exists('assets/images/icon.ico') else None,
) 