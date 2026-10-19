# Dictatore

Offline push-to-talk speech-to-text CLI for Linux.

> **Press a key. Speak. Pause. Text appears.**

No cloud, no telemetry, no always-listening mic. Microphone active only during dictation.

## Quick Start

```bash
# 1. Dependencies
pip install vosk
sudo apt install pipewire-bin xdotool        # Debian/Ubuntu (pw-cat lives in pipewire-bin)
sudo dnf install pipewire-utils xdotool      # Fedora

# 2. Install the command itself (provides the `dictatore` executable)
pip install .

# 3. Download a model (~/.local/share/dictatore/models/en-us)
mkdir -p ~/.local/share/dictatore/models
# easiest: ./scripts/download-model.sh
# or manually: download from https://alphacephei.com/vosk/models, then:
mv ~/Downloads/vosk-model-small-en-us-0.15 ~/.local/share/dictatore/models/en-us

# 4. Verify
dictatore doctor        # or: python -m dictatore doctor
```

## Usage

```bash
dictatore           # Speak, pause to emit, Ctrl+C to quit
dictatore doctor    # Verify dependencies and installation
dictatore config    # Open configuration file
dictatore models    # List installed models
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
├── hotkeys.py       # global shortcut handling (reserved; not used by the main loop)
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
pip install -e ".[test]"     # or: python -m pip install pytest
python -m pytest tests/ -q
```

43 unit tests covering config, events, the state machine, normalize, numbers, plugins, output, and recorder.

The recognizer, overlay, daemon, and main recording loop require vosk/tkinter plus a model; use the Quick Start steps and `dictatore doctor` to verify those.

## How It Works

Dictatore launches, opens the mic, and streams audio to VOSK. When you pause speaking, silence detection triggers after `TIMEOUT` seconds, the recognized text is normalized, numbers are converted, your `transform()` hook and plugins run, and the result is emitted via the chosen output driver. The loop continues until Ctrl+C.

A 0.5-second emit cooldown prevents duplicate emissions from tail audio. Inter-word gaps from VOSK word timestamps insert commas (>0.3s) and periods (>0.7s) automatically.

## Troubleshooting

`dictatore doctor` reports what's missing; exit code is non-zero when anything required is unfixed:

- **No model found** — download per Quick Start, or set `MODEL = "<dir-name>"` in config to match the directory you extracted.
- **Recording backend not found** — install `pipewire-bin` (Debian/Ubuntu) or `pipewire-utils` (Fedora) for `pw-cat`, `pulseaudio-utils` for `parec`, or `alsa-utils` for `arecord`; set `RECORDER` to match what you install.
- **Output driver not found** — `xdotool` for X11, `wtype` for Wayland; use `OUTPUT = "stdout"` for testing.
- **pactl not installed** — informational only; the audio-server check is skipped and dictation still works.
- **Overlay doesn't appear** — tkinter is required (`sudo apt install python3-tk` on Debian/Ubuntu), or set `SHOW_OVERLAY = False`.
