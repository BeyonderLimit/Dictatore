#!/usr/bin/env bash
# One-shot installer for dictatore on Debian/Ubuntu (PEP 668-safe).
#
# Creates a persistent venv at ~/.local/share/dictatore/venv, installs vosk,
# webrtcvad-wheels, and the dictatore package into it, and puts a `dictatore`
# command on PATH (~/.local/bin/dictatore) so window-manager hotkeys work.
#
# Usage: ./scripts/install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${HOME}/.local/share/dictatore/venv"
BIN_LINK="${HOME}/.local/bin/dictatore"

for tool in python3 wget unzip; do
    if ! command -v "$tool" >/dev/null; then
        echo "Error: required tool '$tool' not found in PATH" >&2
        exit 1
    fi
done

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Error: python3-venv is missing. Install it with:" >&2
    echo "  sudo apt install python3-venv" >&2
    exit 1
fi

if [ ! -d "$VENV" ]; then
    echo "Creating venv at $VENV"
    python3 -m venv "$VENV"
fi
PIP="$VENV/bin/pip"
"$PIP" install --upgrade pip

echo "Installing dependencies and the dictatore package"
"$PIP" install --upgrade vosk webrtcvad-wheels
(cd "$REPO_DIR" && "$PIP" install .)

mkdir -p "$(dirname "$BIN_LINK")"
if [ -L "$BIN_LINK" ] && [ "$(readlink "$BIN_LINK")" = "$VENV/bin/dictatore" ]; then
    echo "Command link up to date: $BIN_LINK"
elif [ -e "$BIN_LINK" ]; then
    echo "Warning: $BIN_LINK already exists and is not our shim — leaving it alone." >&2
    echo "  Bind your hotkey to $VENV/bin/dictatore instead." >&2
else
    ln -s "$VENV/bin/dictatore" "$BIN_LINK"
    echo "Created $BIN_LINK -> $VENV/bin/dictatore"
fi

echo
echo "Install complete. Next:"
echo "  ./scripts/setup.sh     # models + base config"
echo "  dictatore doctor"
