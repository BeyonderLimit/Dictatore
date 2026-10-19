#!/usr/bin/env bash
# Set up dictatore: install two English models (small default + accurate
# larger option) and write a base configuration file.
#
# Usage:
#   ./scripts/setup.sh                       # install the default model pair
#   ./scripts/setup.sh vosk-model-small-es-0.42   # install one or more custom zips
#
# With no arguments, installs:
#   vosk-model-small-en-us-0.15  -> ~/.local/share/dictatore/models/en-us
#   vosk-model-en-us-0.22-lgraph -> ~/.local/share/dictatore/models/en-us-0.22
#
# Custom models are installed to ~/.local/share/dictatore/models/<zip basename>;
# point MODEL = "<basename>" at whichever you want in config.
#
# An existing config.py is never overwritten.
set -euo pipefail

MODELS_DIR="${HOME}/.local/share/dictatore/models"
CONFIG_DIR="${HOME}/.config/dictatore"
CONFIG_FILE="${CONFIG_DIR}/config.py"
BASE_URL="https://alphacephei.com/vosk/models"

for tool in wget unzip; do
    if ! command -v "$tool" >/dev/null; then
        echo "Error: required tool '$tool' not found in PATH" >&2
        exit 1
    fi
done

install_model() {  # $1 = zip name on alphacephei, $2 = target dir name
    local zip_name="$1" target="$2"
    local url="${BASE_URL}/${zip_name}.zip"
    local dest="${MODELS_DIR}/${target}"
    local tmp
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' RETURN

    if [ -d "$dest/am" ]; then
        echo "Skip: $target already installed at $dest"
        return 0
    fi

    mkdir -p "$MODELS_DIR"
    echo "Downloading $zip_name -> $dest"
    wget -q --show-progress "$url" -O "$tmp/model.zip"

    unzip -q "$tmp/model.zip" -d "$tmp"
    local extracted
    extracted="$(find "$tmp" -maxdepth 1 -type d -name "${zip_name%.zip}*" | head -1)"
    if [ -z "$extracted" ]; then
        echo "Error: expected extracted directory for $zip_name not found" >&2
        return 1
    fi
    if [ -e "$dest" ]; then
        echo "Error: $dest already exists but is incomplete — remove it and re-run" >&2
        return 1
    fi
    mv "$extracted" "$dest"
    echo "Installed: $dest"
}

write_base_config() {
    if [ -e "$CONFIG_FILE" ]; then
        echo "Keep: existing config at $CONFIG_FILE"
        return 0
    fi
    mkdir -p "$CONFIG_DIR"
    echo "Writing base config to $CONFIG_FILE"
    cat > "$CONFIG_FILE" <<'EOF'
# Dictatore configuration — edit any value, then run: dictatore doctor

HOTKEY = "Super+D"                 # configure the binding in your WM/DE
TIMEOUT = 2.5                      # silence threshold before emitting (sec)
SILENCE_RMS_THRESHOLD = 3000       # raise if silence is never detected
MAX_RECORDING_SECONDS = 60         # safety limit
ENABLE_DIGITS = True
OUTPUT = "xdotool"                 # xdotool | wtype | stdout | clipboard
MODEL = "en-us"                    # dir name under ~/.local/share/dictatore/models
RECORDER = "pw-cat"                # pw-cat | parec | arecord

SHOW_OVERLAY = True
OVERLAY_POSITION = "top-center"
OVERLAY_FONT_SIZE = 14
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 60

# Optional text transform hook:
# def transform(text):
#     return text.replace("linux", "Linux")
EOF
    echo "Base config written"
}

if [ "$#" -gt 0 ]; then
    for zip_name in "$@"; do
        install_model "$zip_name" "$zip_name"
    done
else
    install_model "vosk-model-small-en-us-0.15" "en-us"
    install_model "vosk-model-en-us-0.22-lgraph" "en-us-0.22"
fi

write_base_config

echo
echo "Setup complete. Optional next steps:"
echo "  - Try the larger, more accurate model: set MODEL = \"en-us-0.22\" in $CONFIG_FILE"
echo "  - Verify: dictatore doctor"
