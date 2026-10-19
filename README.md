# Dictatore

Offline push-to-talk speech-to-text CLI for Linux.

> **Press a key. Speak. Pause. Text appears.**

No cloud, no telemetry, no always-listening mic. Microphone active only during dictation.

## Quick Start

```bash
# 1. System dependencies
sudo apt install pipewire-bin xdotool python3-venv      # Debian/Ubuntu
# sudo dnf install pipewire-utils xdotool                # Fedora

# 2. Install into a managed venv and put `dictatore` on PATH
#    (Debian 12+ blocks system-wide pip — PEP 668 — install.sh handles it)
./scripts/install.sh

# 3. Download models and write a base config (easiest path)
./scripts/setup.sh
# installs two models: the fast small one (default) and the larger, more
# accurate en-us-0.22, and writes ~/.config/dictatore/config.py
#
# or manually:
mkdir -p ~/.local/share/dictatore/models
./scripts/download-model.sh          # downloads the accurate 0.22-lgraph model
# https://alphacephei.com/vosk/models — e.g. small model:
mv ~/Downloads/vosk-model-small-en-us-0.15 ~/.local/share/dictatore/models/en-us

# 4. Verify
dictatore doctor
# (or: ~/.local/share/dictatore/venv/bin/python -m dictatore doctor)
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

`scripts/install.sh` places the command in `~/.local/bin/dictatore` (on the default PATH in Debian/Ubuntu desktops). Desktop shortcut tools resolve commands from the session PATH as it was at login, so log out/in once after installing — or bind the absolute path `~/.local/bin/dictatore` in the shortcut.

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

VAD = "webrtc"                   # webrtc | rms | off (off feeds all audio)
VAD_AGGRESSIVENESS = 3           # 0 lenient .. 3 strict; raise if breath still passes
TRANSCRIPT_FILE = "~/.local/share/dictatore/transcript.txt"

SHOW_OVERLAY = True
OVERLAY_POSITION = "top-center"
OVERLAY_FONT_SIZE = 14
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 60
```

Optional `transform(text)` hook and `~/.config/dictatore/plugins/*.py` plugins run in filename order after normalization.

### Voice activity detection

VOSK hallucinates phantom filler words ("the", "and have") when breath or
background noise reaches the recognizer. Dictatore gates the audio with a
VAD: the recognizer only receives speech — plus a short pre-roll and tail
so word onsets and endings survive.

- `VAD = "webrtc"` — Google's WebRTC VAD (needs `pip install webrtcvad-wheels`); strictest and recommended. `VAD_AGGRESSIVENESS` 0–3; **3** is most strict (recommended default — raise it if breath still slips through, lower it if words start getting clipped).
- `VAD = "rms"` — pure‑Python energy gate using `SILENCE_RMS_THRESHOLD`; no extra dependency, less reliable on noisy rooms.
- `VAD = "off"` — no gating; phantom words may re-appear.

### Where your dictation is saved

Every emission is appended, one timestamped line each, to
`~/.local/share/dictatore/transcript.txt` (configurable via
`TRANSCRIPT_FILE`; set it to `None` or `""` to disable logging). This is the
only place dictated text is stored: it happens locally, audio is never
written to disk, and nothing is transmitted anywhere. Delete the file or its
contents whenever you want — no history is kept anywhere else. If the target
input method types into an app (xdotool/wtype), that app's own save behavior
is separate from this log.

## Pipeline

```
Recorder → VAD → VOSK → Normalize → Number Conversion → transform() → Plugins → Output
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
├── vad.py           # voice-activity gating (webrtc / rms), pre-roll + hangover
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

54 unit tests covering config, events, the state machine, normalize, numbers, plugins, output, recorder, and VAD.

The recognizer, overlay, daemon, and main recording loop require vosk/tkinter plus a model; use the Quick Start steps and `dictatore doctor` to verify those.

## How It Works

Dictatore launches, opens the mic, and streams audio through the VAD to VOSK — non-speech audio (breath, background noise) is dropped before the recognizer sees it, preventing phantom "the"-type hallucinations. When you pause speaking, silence detection triggers after `TIMEOUT` seconds, the recognized text is normalized, numbers are converted, your `transform()` hook and plugins run, and the result is emitted via the chosen output driver. The loop continues until Ctrl+C.

A 0.5-second emit cooldown prevents duplicate emissions from tail audio. Inter-word gaps from VOSK word timestamps insert commas (>0.3s) and periods (>0.7s) automatically.

## Troubleshooting

`dictatore doctor` reports what's missing; exit code is non-zero when anything required is unfixed:

- **No model found** — download per Quick Start, or set `MODEL = "<dir-name>"` in config to match the directory you extracted.
- **Recording backend not found** — install `pipewire-bin` (Debian/Ubuntu) or `pipewire-utils` (Fedora) for `pw-cat`, `pulseaudio-utils` for `parec`, or `alsa-utils` for `arecord`; set `RECORDER` to match what you install.
- **Output driver not found** — `xdotool` for X11, `wtype` for Wayland; use `OUTPUT = "stdout"` for testing.
- **pactl not installed** — informational only; the audio-server check is skipped and dictation still works.
- **Overlay doesn't appear** — tkinter is required (`sudo apt install python3-tk` on Debian/Ubuntu), or set `SHOW_OVERLAY = False`.
- **`error: externally-managed-environment`** — Debian 12+ blocks system-wide `pip`. Don't use `--break-system-packages`; run `./scripts/install.sh`, which installs into `~/.local/share/dictatore/venv` and puts `dictatore` in `~/.local/bin`.
- **Word beginnings/endings clipped** — lower `VAD_AGGRESSIVENESS` (3 → 2 or 1), or set `VAD = "off"` to compare.
- **Breath still produces phantom words** — confirm `VAD` is not `"off"`, keep `VAD_AGGRESSIVENESS` at 3, and lower the microphone gain: clipping mic input (RMS near 32768) makes even strict VAD read noise as speech.
