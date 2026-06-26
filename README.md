# Dictatore

Offline push-to-talk speech-to-text CLI for Linux.

> **Press a key. Speak. Pause. Text appears.**

No cloud, no telemetry, no always-listening mic. Microphone active only during dictation.

## Quick Start

```bash
# Dependencies
pip install vosk
sudo apt install pipewire-utils xdotool

# Download a model
mkdir -p ~/.local/share/dictatore/models
# https://alphacephei.com/vosk/models
mv ~/Downloads/vosk-model-small-en-us-0.15 ~/.local/share/dictatore/models/en-us

# Verify
python -m dictatore doctor
```

## Usage

```bash
python -m dictatore           # Speak, pause to emit, Ctrl+C to quit
python -m dictatore doctor    # Verify dependencies and installation
python -m dictatore config    # Open configuration file
python -m dictatore models    # List installed models
```

Set `OUTPUT = "stdout"` in config for terminal testing.

## Hotkey Setup

Bind `dictatore` (or `python -m dictatore`) to a key in your window manager. When pressed, the mic opens and records until you pause speaking.

**Sway/i3:**
```
bindsym $mod+d exec dictatore
```

**KDE:** System Settings → Shortcuts → Custom Shortcuts → New → Global Shortcut → Command/URL

**GNOME:** Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts → Add

## Configuration

`~/.config/dictatore/config.py`:

```python
TIMEOUT = 2.5                    # silence threshold (seconds)
SILENCE_RMS_THRESHOLD = 3000     # raise if mic never stops detecting silence
MAX_RECORDING_SECONDS = 60       # safety limit
ENABLE_DIGITS = True
OUTPUT = "xdotool"               # xdotool | wtype | stdout | clipboard
MODEL = "en-us"
RECORDER = "pw-cat"              # pw-cat | parec | arecord

SHOW_OVERLAY = True
OVERLAY_POSITION = "top-center"
OVERLAY_FONT_SIZE = 14
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 60
```

Optional `transform(text)` hook and `~/.config/dictatore/plugins/*.py` plugins run in filename order after normalization.

## Pipeline

```
Recorder → VOSK → Normalize → Number Conversion → transform() → Plugins → Output
```

Overlay shows partial recognition while recording. Output drivers: xdotool (X11), wtype (Wayland), stdout, clipboard.

## Package Layout

```
dictatore/
├── main.py          # recording loop
├── cli.py           # command routing
├── config.py        # config loading
├── events.py        # event bus
├── state.py         # state machine
├── hotkeys.py       # global shortcut registration
├── recorder.py      # audio capture (pw-cat / parec / arecord)
├── recognizer.py    # VOSK speech engine
├── normalize.py     # text normalization + punctuation from word gaps
├── numbers.py       # spoken→digit conversion
├── overlay.py       # floating partial-recognition window
├── output.py        # output drivers
├── plugins.py       # plugin loader
├── daemon.py        # fast mode background process
└── doctor.py        # diagnostics
```

## Testing

```bash
python -m pytest tests/
```

48 unit tests covering config, events, state machine, normalize, numbers, plugins, output, recorder.

## How It Works

Dictatore launches, opens the mic, and streams audio to VOSK. When you pause speaking, silence detection triggers after `TIMEOUT` seconds, the recognized text is normalized, numbers are converted, your `transform()` hook and plugins run, and the result is emitted via the chosen output driver. The loop continues until Ctrl+C.

A 1-second emit cooldown prevents duplicate emissions from tail audio. Inter-word gaps from VOSK word timestamps insert commas (>0.3s) and periods (>0.7s) automatically.
