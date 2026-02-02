#!/bin/bash
# Download Vosk speech recognition model for Raspberry Pi Zero W
# Uses the small English model (0.15) which is lightweight and suitable for Pi Zero W

set -e

MODEL_NAME="vosk-model-small-en-us-0.15"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
MODEL_DIR="vosk-model"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${PROJECT_ROOT}/${MODEL_DIR}"

echo "Downloading Vosk model for Brain Ball..."
echo "Model: ${MODEL_NAME}"
echo "Target directory: ${TARGET_DIR}"

# Check if model already exists
if [ -d "${TARGET_DIR}" ] && [ -f "${TARGET_DIR}/am/final.mdl" ]; then
    echo "Model already exists at ${TARGET_DIR}"
    echo "Skipping download. To re-download, delete the ${MODEL_DIR} directory first."
    exit 0
fi

# Create target directory
mkdir -p "${TARGET_DIR}"

# Download model
echo "Downloading from ${MODEL_URL}..."
cd "${PROJECT_ROOT}"
TEMP_ZIP=$(mktemp)
curl -L -o "${TEMP_ZIP}" "${MODEL_URL}" || {
    echo "Error: Failed to download model"
    rm -f "${TEMP_ZIP}"
    exit 1
}

# Extract model
echo "Extracting model..."
unzip -q "${TEMP_ZIP}" -d "${TARGET_DIR}" || {
    echo "Error: Failed to extract model"
    rm -f "${TEMP_ZIP}"
    exit 1
}

# Move model files if they're in a subdirectory
if [ -d "${TARGET_DIR}/${MODEL_NAME}" ]; then
    echo "Moving model files to target directory..."
    mv "${TARGET_DIR}/${MODEL_NAME}"/* "${TARGET_DIR}/"
    rmdir "${TARGET_DIR}/${MODEL_NAME}"
fi

# Clean up
rm -f "${TEMP_ZIP}"

# Verify model
if [ -f "${TARGET_DIR}/am/final.mdl" ]; then
    echo "✓ Model downloaded successfully!"
    echo "Model location: ${TARGET_DIR}"
else
    echo "Error: Model verification failed. Expected file not found: ${TARGET_DIR}/am/final.mdl"
    exit 1
fi
