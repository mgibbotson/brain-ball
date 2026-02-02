#!/usr/bin/env python3
"""Download Vosk speech recognition model for Raspberry Pi Zero W.

Uses the small English model (0.15) which is lightweight and suitable for Pi Zero W.
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
from pathlib import Path

MODEL_NAME = "vosk-model-small-en-us-0.15"
MODEL_URL = f"https://alphacephei.com/vosk/models/{MODEL_NAME}.zip"
MODEL_DIR = "vosk-model"


def main():
    """Download and extract Vosk model."""
    # Get project root (parent of scripts directory)
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    target_dir = project_root / MODEL_DIR
    
    print("Downloading Vosk model for Brain Ball...")
    print(f"Model: {MODEL_NAME}")
    print(f"Target directory: {target_dir}")
    
    # Check if model already exists
    model_file = target_dir / "am" / "final.mdl"
    if model_file.exists():
        print(f"Model already exists at {target_dir}")
        print(f"Skipping download. To re-download, delete the {MODEL_DIR} directory first.")
        return 0
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Download model
    print(f"Downloading from {MODEL_URL}...")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_zip = temp_file.name
            urllib.request.urlretrieve(MODEL_URL, temp_zip)
    except Exception as e:
        print(f"Error: Failed to download model: {e}")
        return 1
    
    # Extract model
    print("Extracting model...")
    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
    except Exception as e:
        print(f"Error: Failed to extract model: {e}")
        os.unlink(temp_zip)
        return 1
    
    # Move model files if they're in a subdirectory
    model_subdir = target_dir / MODEL_NAME
    if model_subdir.exists():
        print("Moving model files to target directory...")
        for item in model_subdir.iterdir():
            dest = target_dir / item.name
            if dest.exists():
                if dest.is_dir():
                    import shutil
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            item.rename(dest)
        model_subdir.rmdir()
    
    # Clean up
    os.unlink(temp_zip)
    
    # Verify model
    if model_file.exists():
        print("✓ Model downloaded successfully!")
        print(f"Model location: {target_dir}")
        return 0
    else:
        print(f"Error: Model verification failed. Expected file not found: {model_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
