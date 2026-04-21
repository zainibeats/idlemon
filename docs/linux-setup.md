# Running IdleMon on Linux (From Source)

IdleMon is a Python + PySide6 (Qt6) application. The source code is cross-platform and can run on Linux with minimal setup.

## Prerequisites

- Python 3.9 or newer
- A desktop environment with X11 or Wayland display server
- Audio support (PulseAudio or PipeWire) for sound effects

## Installation

### 1. Install system dependencies

PySide6 requires certain Qt6/OpenGL runtime libraries. Install them for your distribution:

**Debian/Ubuntu:**
```bash
sudo apt install python3 python3-pip python3-venv \
    libgl1 libegl1 libxkbcommon0 libdbus-1-3 \
    libxcb-xinerama0 libxcb-cursor0
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip \
    mesa-libGL mesa-libEGL libxkbcommon dbus-libs \
    xcb-util-cursor
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip \
    mesa libxkbcommon dbus xcb-util-cursor
```

**Alpine Linux:**
```bash
apk add python3 py3-pip \
    mesa-gl mesa-egl libxkbcommon dbus-libs xcb-util-cursor
```

### 2. Create a virtual environment and install Python dependencies

```bash
cd /path/to/idlemon
python3 -m venv venv
source venv/bin/activate
pip install PySide6>=6.8.0
```

### 3. Fix config path separator

The default `config.json` uses Windows-style backslashes in the background image path. Update it to use forward slashes:

**Before:**
```json
"background_image": "assets\\images\\default_background.jpg"
```

**After:**
```json
"background_image": "assets/images/default_background.jpg"
```

You can do this with sed:
```bash
sed -i 's|\\\\|/|g' config.json
```

### 4. Run the application

```bash
source venv/bin/activate
cd src
python3 main.py
```

## Troubleshooting

### Qt platform plugin error
If you see `Could not find the Qt platform plugin "xcb"`, you may be missing X11/xcb libraries:
```bash
# Debian/Ubuntu
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-render-util0

# Or try using the Wayland backend instead
export QT_QPA_PLATFORM=wayland
```

### No sound
QSoundEffect requires a working audio backend. Ensure PulseAudio or PipeWire is running:
```bash
# Check if PulseAudio/PipeWire is running
pactl info

# Debian/Ubuntu - install if missing
sudo apt install pulseaudio
```

### Blank or black window
This can indicate missing OpenGL drivers:
```bash
# Debian/Ubuntu
sudo apt install mesa-utils libgl1-mesa-dri

# Verify OpenGL works
glxinfo | grep "OpenGL renderer"
```

### Wayland display issues
If running under Wayland and experiencing rendering problems, try forcing X11:
```bash
export QT_QPA_PLATFORM=xcb
python3 main.py
```
