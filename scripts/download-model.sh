#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="vosk-model-en-us-0.22-lgraph"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
MODELS_DIR="${HOME}/.local/share/dictatore/models"
TARGET_DIR="${MODELS_DIR}/en-us"
TMPDIR="$(mktemp -d)"

if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/am" ]; then
    echo "Model already exists at $TARGET_DIR"
    rm -rf "$TMPDIR"
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
    rm -rf "$TMPDIR"
    exit 1
fi

mkdir -p "$MODELS_DIR"
mv "$EXTRACTED" "$TARGET_DIR"

rm -rf "$TMPDIR"
echo "Model installed at $TARGET_DIR"
