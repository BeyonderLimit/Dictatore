# Dictatore 2.0 — Project Plan & Deployment Architecture


## Vision

Dictatore is an offline, keyboard-driven speech-to-text utility for Linux. Inspired by Nerd-dictation (https://github.com/ideasman42/nerd-dictation)

It is designed around one principle:

> **Press a key. Speak. Release. Your words appear.**

No cloud services.

No telemetry.

No always-listening microphone.

No desktop environment dependency.

The microphone is only active while the user explicitly requests recording.

---

# Goals

## Primary Goals

* Offline speech recognition
* Desktop environment independent
* Wayland and X11 support
* Zero CPU while idle
* Simple installation
* Python configurable
* Small codebase
* Easily hackable

---

## User Modes

### Simple (Default)

No daemon.

Program starts when recording begins.

Program exits after processing.

Advantages

* Zero RAM while idle
* Zero background processes
* Extremely simple architecture

---

### Fast Mode

Background daemon.

Speech model remains loaded.

Microphone remains disabled.

Advantages

* Instant activation
* Better for heavy daily use

---

# User Workflow

## Tap Mode

Tap hotkey

↓

Begin recording

↓

Silence timeout

↓

Recognize

↓

Process text

↓

Output

---

## Push-to-Talk

Hold hotkey

↓

Record

↓

Release key

↓

Recognize

↓

Output

---

## Hold Mode

Hold hotkey

↓

Press Hold shortcut

↓

Recording locks

↓

Continue speaking

↓

Press Hold shortcut

↓

Recognize

↓

Output

Suitable for meetings, interviews, lectures and long dictation.

---

# Runtime Pipeline

```
Hotkey
    │
    ▼
Recorder
    │
    ▼
Speech Engine
    │
    ▼
Normalizer
    │
    ▼
Number Parser
    │
    ▼
User Transform
    │
    ▼
Plugins
    │
    ▼
Output Driver
```

Overlay listens independently for recognition events.

---

# Runtime Components

## CLI

Responsible for installation, diagnostics and configuration.

Commands

```
dictatore install

dictatore doctor

dictatore config

dictatore models

dictatore daemon
```

Recording is entirely hotkey driven.

---

## Hotkey Manager

Responsibilities

* register global shortcut
* detect press
* detect release
* detect hold toggle

Events

```
key_down

key_up

hold_toggle
```

---

## Recorder

Abstract audio capture.

Interface

```
start(callback)

stop()
```

Supported backends

* pw-cat
* parec
* arecord
* sox

---

## Speech Engine

Responsibilities

* initialize recognizer
* stream audio
* emit partial text
* emit final text

Interface

```
start()

feed(audio)

stop()
```

Future engines

* VOSK
* whisper.cpp

---

## Overlay

Subscribes to recognition events.

Receives

```
partial_text()

final_text()
```

Responsibilities

* display partial recognition
* auto-hide
* never steal focus

---

## Text Pipeline

Stages

```
Normalize

↓

Number Conversion

↓

User transform()

↓

Plugin chain

↓

Output
```

---

## Number Parser

Supports

```
three hundred

↓

300
```

```
two four six eight

↓

2468
```

```
three million five hundred sixty second

↓

3,000,562nd
```

Future

* decimals
* fractions
* percentages
* currencies
* dates
* times

---

## Output Drivers

```
Xdotool

Wtype

Stdout

Clipboard
```

---

## Plugin Loader

Search path

```
~/.config/dictatore/plugins/
```

Plugin interface

```python
def transform(text):
    return text
```

Plugins execute sequentially.

---

# Event System

Every component communicates using events.

```
Key Down

↓

Recorder Started

↓

Audio Chunk

↓

Partial Recognition

↓

Overlay Update

↓

Final Recognition

↓

Text Pipeline

↓

Output Driver

↓

Idle
```

No component directly controls another.

---

# Directory Layout

Repository

```
dictatore/

├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── install.py
├── build.sh
├── package.sh
├── scripts/
│
├── dictatore/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── events.py
│   ├── state.py
│   ├── hotkeys.py
│   ├── recorder.py
│   ├── recognizer.py
│   ├── numbers.py
│   ├── normalize.py
│   ├── overlay.py
│   ├── output.py
│   ├── plugins.py
│   ├── daemon.py
│   └── doctor.py
│
├── assets/
│
├── docs/
│
├── examples/
│
└── packaging/
```

Although internally modular, it can still be bundled into a single executable with PyInstaller or Shiv if desired.

---

# User Configuration

```
~/.config/dictatore/

config.py

plugins/
```

Example

```python
HOTKEY = "Super+D"

HOLD_HOTKEY = "Super+Shift+D"

SHOW_OVERLAY = True

OUTPUT = "xdotool"

ENABLE_DIGITS = True
```

---

# Overlay Configuration

```
SHOW_OVERLAY=True

POSITION="top-center"

FONT_SIZE=14

WIDTH=60

OPACITY=0.9
```

---

# Installer

Interactive installer.

## Step 1

Choose mode

```
Simple (recommended)

Fast
```

---

## Step 2

Choose audio backend

```
pw-cat

parec

arecord

sox
```

---

## Step 3

Choose output

```
xdotool

wtype

stdout

clipboard
```

---

## Step 4

Choose hotkeys

Example

```
Push-to-talk

Super+D
```

```
Hold

Super+Shift+D
```

---

## Step 5

Overlay

```
Enable overlay?

[Y/n]
```

---

## Step 6

Download model (optional)

Offer language selection.

---

# Deployment Strategy

## Development

Run directly from source.

```
python -m dictatore
```

---

## Standalone Installer

Provide

```
install.py
```

Responsibilities

* dependency checks
* create config
* install hotkeys
* install desktop files
* download language models
* create daemon service (Fast mode)

---

## PyPI

```
pip install dictatore
```

Post-install

```
dictatore install
```

---

## Distribution Packages

Provide native packages.

```
.deb

.rpm

.pkg.tar.zst
```

---

## Portable Binary

Bundle Python runtime.

Produce

```
dictatore
```

Single executable.

---

## Source Release

Git clone.

Run

```
python install.py
```

---

# Release Pipeline

```
Git Tag

↓

GitHub Release

↓

CI Build

↓

Run Tests

↓

Create Python Wheel

↓

Create Standalone Binary

↓

Build Debian Package

↓

Build RPM

↓

Build Arch Package

↓

Publish Release
```

---

# Testing

## Unit Tests

* number parser
* normalizer
* plugin loader
* event system
* configuration

---

## Integration Tests

* recorder
* recognizer
* output drivers
* overlay

---

## Manual Tests

* X11
* Wayland
* PipeWire
* PulseAudio
* ALSA

---

# Future Roadmap

## Version 2.1

* Whisper.cpp backend
* Multiple language models
* Overlay themes

---

## Version 2.2

* Voice commands
* Custom vocabularies
* Macro expansion

---

## Version 3.0

* Live punctuation
* Grammar correction (offline)
* Local LLM integration
* Context-aware formatting

---

# Design Philosophy

Dictatore should remain a small Unix utility rather than a full desktop assistant.

Its responsibilities are intentionally narrow:

1. Capture speech only when explicitly requested.
2. Convert speech to text entirely offline.
3. Allow users to transform that text with simple Python code.
4. Display optional live feedback while recording.
5. Deliver the final text to the chosen output destination.
6. Exit cleanly—or sleep efficiently in Fast mode—without consuming unnecessary resources.

Everything else should be implemented as optional extensions, preserving a fast, understandable, and maintainable core.
