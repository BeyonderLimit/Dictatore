#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="vosk-model-en-us-0.22-lgraph"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
MODELS_DIR="${HOME}/.local/share/dictatore/models"
TARGET_DIR="${MODELS_DIR}/en-us"
TMPDIR="$(mktemp -d)"

trap 'rm -rf "$TMPDIR"' EXIT

for tool in wget unzip; do
    if ! command -v "$tool" >/dev/null; then
        echo "Error: required tool '$tool' not found in PATH" >&2
        exit 1
    fi
done

if [ -d "$TARGET_DIR/am" ]; then
    echo "Model already exists at $TARGET_DIR"
    exit 0
fi

mkdir -p "$MODELS_DIR"

echo "Downloading $MODEL_NAME ..."
wget -q --show-progress "$MODEL_URL" -O "$TMPDIR/model.zip"

echo "Extracting ..."
unzip -q "$TMPDIR/model.zip" -d "$TMPDIR"

EXTRACTED=$(find "$TMPDIR" -maxdepth 1 -type d -name "${MODEL_NAME}*" | head -1)
if [ -z "$EXTRACTED" ]; then
    echo "Error: expected extracted directory not found" >&2
    exit 1
fi

mv "$EXTRACTED" "$TARGET_DIR"

echo "Model installed at $TARGET_DIR"
