# Dictatore — User Instructions

> **Tap. Hold. Speak. Text appears.**

## Quick Start

```bash
pip install vosk
sudo apt install pipewire-utils xdotool   # Debian/Ubuntu
sudo dnf install pipewire-utils xdotool   # Fedora

# Download a VOSK model
mkdir -p ~/.local/share/dictatore/models
# https://alphacephei.com/vosk/models — e.g. vosk-model-small-en-us-0.15
mv ~/Downloads/vosk-model-* ~/.local/share/dictatore/models/en-us

dictatore doctor       # verify setup
```

## Usage

| Mode | Action | Best for |
|---|---|---|
| **Tap** | Tap the hotkey. Speak. Silence stops recording. | Short sentences |
| **Push-to-Talk** | Hold the hotkey. Speak. Release. | Normal dictation |
| **Hold Lock** | Start Push-to-Talk, press hold shortcut. Recording locks. Press hold shortcut again to stop. | Long dictation, meetings |

While recording, a small overlay shows partial recognition in real time. It disappears on release — only the final text is typed.

## Commands

| Command | Action |
|---|---|
| `dictatore` | Hotkey entry point. Tap = silence-detect. Hold = push-to-talk. |
| `dictatore daemon` | Start background daemon (Fast mode — pre-loads model) |
| `dictatore doctor` | Verify dependencies, model, backends, permissions |
| `dictatore models` | List installed models |
| `dictatore install` | Interactive setup |
| `dictatore config` | Open config file |

## Configuration

`~/.config/dictatore/config.py`:

```python
HOTKEY = "Super+D"                 # documented default; configure in your WM/DE
TIMEOUT = 2.5                      # silence threshold for Tap mode (seconds)
SILENCE_RMS_THRESHOLD = 3000       # raise if mic never stops detecting silence
MAX_RECORDING_SECONDS = 60         # safety limit
ENABLE_DIGITS = True
OUTPUT = "xdotool"                 # xdotool | wtype | stdout | clipboard
MODEL = "en-us"
RECORDER = "pw-cat"                # pw-cat | parec | arecord | sox

SHOW_OVERLAY = True
OVERLAY_POSITION = "top-center"
OVERLAY_FONT_SIZE = 14
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 60
```

### Transform Hook

```python
def transform(text):
    text = text.replace("linux", "Linux")
    return text
```

### Plugins

Each `.py` file in `~/.config/dictatore/plugins/` exports `transform(text)`. Run in filename order after the config hook.

## Hotkey Setup

Bind `dictatore` to a key in your window manager. When pressed, it launches dictatore, opens the mic, and records until you pause speaking.

**Sway (Wayland):**
```
bindsym --whole-window $mod+d exec dictatore
```
**i3 (X11):**
```
bindsym Mod4+d exec dictatore
```
**KDE:** System Settings → Shortcuts → Custom Shortcuts → Edit → New → Global Shortcut → Command/URL → set Trigger to `Super+D`, Action to `dictatore`
**GNOME:** Settings → Keyboard → Keyboard Shortcuts → View and Customize Shortcuts → Custom Shortcuts → Add `dictatore`

## Model Setup

1. Download from https://alphacephei.com/vosk/models
2. Extract to `~/.local/share/dictatore/models/<name>`
3. Set `MODEL = "<name>"` in config

## Simple vs Fast Mode

- **Simple (default):** no daemon, zero RAM idle, model loads on demand.
- **Fast:** `dictatore daemon` keeps model in memory for instant activation. Same hotkey UX.
