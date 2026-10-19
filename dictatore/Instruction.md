# Dictatore — User Instructions

> **Tap. Hold. Speak. Text appears.**

## Quick Start

```bash
sudo apt install pipewire-bin xdotool python3-venv   # Debian/Ubuntu
sudo dnf install pipewire-utils xdotool      # Fedora

# Install into a managed venv + create the `dictatore` command (PEP 668-safe)
./scripts/install.sh

# Download two models + write a base config
./scripts/setup.sh

dictatore doctor       # verify setup
```

## Usage

Dictation runs until you pause speaking, then the recognized text is emitted. Bind `dictatore` to a key in your window manager, or run it from a terminal.

While recording, a small overlay shows partial recognition in real time. Overlay disappears on emit — only the final text is typed.

Every emitted utterance is appended to a local transcript file
(`~/.local/share/dictatore/transcript.txt`). Delete it any time; nothing is
transmitted anywhere.

> Tap / Push-to-Talk / Hold Lock modes are documented for a future release and
> are not implemented in v2.0.

## Commands

| Command | Action |
|---|---|
| `dictatore` | Launch continuous dictation — speak, pause to emit, Ctrl+C to quit. |
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
RECORDER = "pw-cat"                # pw-cat | parec | arecord

VAD = "webrtc"                     # webrtc | rms | off — gates breath/noise before VOSK
VAD_AGGRESSIVENESS = 3             # 0 lenient .. 3 strict; raise if breath still passes
TRANSCRIPT_FILE = "~/.local/share/dictatore/transcript.txt"  # set to None to disable

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
- **Fast:** `dictatore daemon` pre-loads the model and serves JSON requests
  (newline-terminated) on `~/.local/share/dictatore/daemon.sock` — actions:
  `recognize` (send raw s16le 16 kHz mono audio as hex), `result`, `quit`. It
  is currently a server API — it is not yet integrated with the hotkey launch
  path.
