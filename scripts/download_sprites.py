#!/usr/bin/env python3
"""Download Stardew Valley animal sprites from stardew-png.github.io.

Downloads all animal sprites and organizes them by animal type.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List

SPRITES_DIR = "sprites/Animals"
BASE_URL = "https://stardew-png.github.io"

# Animal categories and their associated keywords for matching
ANIMAL_CATEGORIES = {
    "cow": ["cow", "cattle", "bovine", "moo"],
    "pig": ["pig", "swine", "hog", "oink"],
    "chicken": ["chicken", "hen", "rooster", "cluck"],
    "sheep": ["sheep", "lamb", "ewe", "ram", "baa"],
    "horse": ["horse", "pony", "mare", "stallion", "neigh"],
    "duck": ["duck", "quack"],
    "goat": ["goat", "bleat"],
    "dog": ["dog", "puppy", "woof", "bark"],
    "cat": ["cat", "kitten", "meow"],
}


def download_sprite_from_url(url: str, target_path: Path, verbose: bool = False) -> bool:
    """Download a single sprite from a URL.
    
    Args:
        url: URL to download from
        target_path: Path to save the sprite
        verbose: If True, print progress
        
    Returns:
        True if successful, False otherwise
    """
    try:
        urllib.request.urlretrieve(url, target_path)
        # Verify it's a valid PNG
        if target_path.stat().st_size > 100:
            with open(target_path, 'rb') as f:
                header = f.read(8)
                if header[:8] == b'\x89PNG\r\n\x1a\n':
                    return True
                else:
                    target_path.unlink()
                    return False
        else:
            target_path.unlink()
            return False
    except Exception as e:
        if verbose:
            print(f"  Error downloading {url}: {e}")
        if target_path.exists():
            target_path.unlink()
        return False


def download_sprites(project_root: Path = None, verbose: bool = False, progress_callback=None) -> bool:
    """Download Stardew Valley animal sprites from stardew-png.github.io.
    
    Args:
        project_root: Path to project root. If None, auto-detects from script location.
        verbose: If True, print progress messages. If False, silent operation.
        progress_callback: Optional callback function(animal_type, filename, status) for progress updates.
        
    Returns:
        True if sprites were downloaded or already exist, False otherwise.
    """
    if project_root is None:
        script_dir = Path(__file__).parent.resolve()
        project_root = script_dir.parent
    target_dir = project_root / SPRITES_DIR
    
    # Create target directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each animal type
    for animal_type in ANIMAL_CATEGORIES.keys():
        (target_dir / animal_type).mkdir(parents=True, exist_ok=True)
    
    # Check if we already have sprites
    existing_count = 0
    for animal_type in ANIMAL_CATEGORIES.keys():
        animal_dir = target_dir / animal_type
        if animal_dir.exists():
            existing_count += len(list(animal_dir.glob("*.png")))
    
    if existing_count > 0 and verbose:
        print(f"Found {existing_count} existing sprites")
    
    # Download from stardew-png.github.io using the correct URL pattern:
    # https://stardew-png.github.io/data/sprites/Animals/<animal_name>/<frame_number>.png
    downloaded_count = 0
    
    if verbose:
        print("Downloading sprites from stardew-png.github.io...")
        print("URL pattern: https://stardew-png.github.io/data/sprites/Animals/<animal>/<frame>.png")
        print("Note: This may take a while as we fetch all animal sprites.")
    
    # Base URL pattern
    base_url_pattern = f"{BASE_URL}/data/sprites/Animals"
    
    # Animal name variations to try (base name + numbered variants)
    animal_name_variations = {
        "cow": ["cow"],
        "pig": ["pig"],
        "chicken": ["chicken"],
        "sheep": ["sheep"],
        "horse": ["horse"],
        "duck": ["duck"],
        "goat": ["goat"],
        "dog": ["dog", "dog2", "dog3", "dog4", "dog5"],
        "cat": ["cat", "cat2"],
    }
    
    # Try frame numbers from 0 to 30 (most sprites have frames in this range)
    max_frames = 30
    
    for animal_type in ANIMAL_CATEGORIES.keys():
        animal_dir = target_dir / animal_type
        variations = animal_name_variations.get(animal_type, [animal_type])
        
        if verbose:
            print(f"\nDownloading {animal_type} sprites...")
        
        for animal_name in variations:
            frames_downloaded = 0
            consecutive_404s = 0
            max_consecutive_404s = 5  # Stop if we get 5 consecutive 404s
            
            for frame_num in range(max_frames + 1):
                url = f"{base_url_pattern}/{animal_name}/{frame_num}.png"
                filename = f"{animal_name}_{frame_num:02d}.png"
                target_path = animal_dir / filename
                
                if target_path.exists():
                    frames_downloaded += 1
                    consecutive_404s = 0  # Reset counter if file exists
                    continue  # Skip if already exists
                
                try:
                    # Try to download
                    if verbose:
                        print(f"  Downloading {animal_type}/{filename}...", end=" ", flush=True)
                    if progress_callback:
                        progress_callback(animal_type, filename, "downloading")
                    urllib.request.urlretrieve(url, target_path)
                    # Verify it's a valid PNG
                    if target_path.stat().st_size > 100:
                        with open(target_path, 'rb') as f:
                            header = f.read(8)
                            if header[:8] == b'\x89PNG\r\n\x1a\n':
                                downloaded_count += 1
                                frames_downloaded += 1
                                consecutive_404s = 0  # Reset counter on success
                                if verbose:
                                    print(f"✓")
                                if progress_callback:
                                    progress_callback(animal_type, filename, "success")
                                continue
                    
                    # Not a valid PNG, delete it
                    target_path.unlink()
                    consecutive_404s += 1
                    if verbose:
                        print("✗ (invalid PNG)")
                    if progress_callback:
                        progress_callback(animal_type, filename, "failed")
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        consecutive_404s += 1
                        if verbose:
                            print("✗ (404)")
                    else:
                        consecutive_404s = 0  # Reset on other errors
                        if verbose:
                            print(f"✗ (HTTP {e.code})")
                    if progress_callback and e.code != 404:  # Don't callback for 404s (too many)
                        progress_callback(animal_type, filename, "failed")
                    if target_path.exists():
                        target_path.unlink()
                except Exception as e:
                    consecutive_404s += 1
                    if verbose:
                        print(f"✗ ({type(e).__name__})")
                    if progress_callback:
                        progress_callback(animal_type, filename, "failed")
                    if target_path.exists():
                        target_path.unlink()
                
                # Stop if we get too many consecutive 404s
                if consecutive_404s >= max_consecutive_404s:
                    break
            
            if frames_downloaded > 0 and verbose:
                print(f"  Downloaded {frames_downloaded} frames for {animal_name}")
    
    if verbose:
        total_count = sum(len(list((target_dir / animal).glob("*.png"))) 
                          for animal in ANIMAL_CATEGORIES.keys())
        print(f"\nTotal sprites: {total_count}")
    
    # Return True if we have at least some sprites for each animal type
    has_sprites = all(
        len(list((target_dir / animal_type).glob("*.png"))) > 0
        for animal_type in ANIMAL_CATEGORIES.keys()
    )
    
    return has_sprites


def main():
    """CLI entry point for downloading sprites."""
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    print("Stardew Valley Animal Sprites Download")
    print("=" * 50)
    print(f"Target directory: {project_root / SPRITES_DIR}")
    print()
    print("NOTE: Stardew Valley sprites are copyrighted by ConcernedApe.")
    print("Downloading from stardew-png.github.io for educational use.")
    print()
    
    success = download_sprites(project_root, verbose=True)
    
    target_dir = project_root / SPRITES_DIR
    total_count = sum(len(list((target_dir / animal).glob("*.png"))) 
                      for animal in ANIMAL_CATEGORIES.keys())
    
    if success and total_count > 0:
        print(f"\n✓ Successfully downloaded {total_count} sprites!")
        print(f"Sprite location: {target_dir}")
        print("\nSprites organized by animal type:")
        for animal_type in ANIMAL_CATEGORIES.keys():
            count = len(list((target_dir / animal_type).glob("*.png")))
            if count > 0:
                print(f"  {animal_type}: {count} sprite(s)")
        return 0
    elif total_count > 0:
        print(f"\n⚠ Partially downloaded: {total_count} sprites")
        print("Some animal types may be missing sprites.")
        return 0
    else:
        print("\n✗ Download failed.")
        print("The script attempted to download from stardew-png.github.io")
        print("but was unable to access the sprites.")
        print("\nYou can manually place sprite PNG files in:")
        print(f"  {target_dir}/<animal_type>/")
        print("\nAnimal types:", ", ".join(ANIMAL_CATEGORIES.keys()))
        return 1


if __name__ == "__main__":
    sys.exit(main())
