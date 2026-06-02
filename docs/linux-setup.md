# Run IdleMon on Linux

IdleMon is supported on Linux by running from source. There is no Linux binary release in this branch right now.

## Requirements

- Python 3.9 or newer
- A desktop session with X11 or Wayland
- Audio support through PulseAudio or PipeWire

## System Packages

Install the Python basics plus the Qt runtime libraries needed by PySide6.

### Debian or Ubuntu

```bash
sudo apt install python3 python3-pip python3-venv \
    libgl1 libegl1 libxkbcommon0 libdbus-1-3 \
    libxcb-xinerama0 libxcb-cursor0
```

### Fedora

```bash
sudo dnf install python3 python3-pip \
    mesa-libGL mesa-libEGL libxkbcommon dbus-libs \
    xcb-util-cursor
```

### Arch Linux

```bash
sudo pacman -S python python-pip \
    mesa libxkbcommon dbus xcb-util-cursor
```

## Python Environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

From the repository root:

```bash
source .venv/bin/activate
python src/main.py
```

## Notes

- The default `config/config.json` may contain Windows-style separators. IdleMon normalizes those paths at runtime.
- Save data is written to `config/save_data.json` in the project root.

## Troubleshooting

### Qt platform plugin `xcb`

If Qt cannot load the `xcb` platform plugin, install the missing xcb packages:

```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-render-util0
```

If you are on Wayland, you can also try:

```bash
export QT_QPA_PLATFORM=wayland
python src/main.py
```

### No sound

Check that PulseAudio or PipeWire is available:

```bash
pactl info
```

### Blank or black window

Install or verify OpenGL drivers:

```bash
sudo apt install mesa-utils libgl1-mesa-dri
glxinfo | grep "OpenGL renderer"
```
