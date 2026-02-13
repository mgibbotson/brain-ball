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


def download_vosk_model(project_root: Path = None) -> bool:
    """Download and extract Vosk model.
    
    Args:
        project_root: Path to project root. If None, auto-detects from script location.
        
    Returns:
        True if model was successfully downloaded or already exists, False otherwise.
    """
    if project_root is None:
        script_dir = Path(__file__).parent.resolve()
        project_root = script_dir.parent
    target_dir = project_root / MODEL_DIR
    
    print("Downloading Vosk model for Brain Ball...")
    print(f"Model: {MODEL_NAME}")
    print(f"Target directory: {target_dir}")
    
    # Check if model already exists
    model_file = target_dir / "am" / "final.mdl"
    if model_file.exists():
        return True
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Download model
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_zip = temp_file.name
            urllib.request.urlretrieve(MODEL_URL, temp_zip)
    except Exception as e:
        return False
    
    # Extract model
    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
    except Exception as e:
        os.unlink(temp_zip)
        return False
    
    # Move model files if they're in a subdirectory
    model_subdir = target_dir / MODEL_NAME
    if model_subdir.exists():
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
    return model_file.exists()


def main():
    """CLI entry point for downloading Vosk model."""
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    print("Downloading Vosk model for Brain Ball...")
    print(f"Model: {MODEL_NAME}")
    print(f"Target directory: {project_root / MODEL_DIR}")
    
    success = download_vosk_model(project_root)
    
    if success:
        model_file = project_root / MODEL_DIR / "am" / "final.mdl"
        if model_file.exists():
            print("✓ Model downloaded successfully!")
            print(f"Model location: {project_root / MODEL_DIR}")
        else:
            print(f"Model already exists at {project_root / MODEL_DIR}")
        return 0
    else:
        print("Error: Failed to download model")
        return 1


if __name__ == "__main__":
    sys.exit(main())
