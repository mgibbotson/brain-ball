"""Pixel art image assets - Stardew Valley sprites."""

import os
import random
import logging
from typing import Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory for Stardew Valley sprites
SPRITES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sprites", "Animals")


def _load_sprite_image(sprite_path: str) -> Optional[List[List[Tuple[int, int, int]]]]:
    """
    Load a sprite image from file and convert to 2D array of RGB tuples.
    
    Parameters:
        sprite_path: Path to sprite PNG file (relative to SPRITES_DIR or absolute)
        
    Returns:
        2D array of RGB tuples [[(r, g, b), ...], ...], or None if file not found
    """
    try:
        from PIL import Image
    except ImportError:
        logger.error("PIL/Pillow not available - cannot load sprite images")
        return None
    
    # Resolve sprite path
    if os.path.isabs(sprite_path):
        full_path = sprite_path
    elif isinstance(sprite_path, Path):
        full_path = str(sprite_path)
    else:
        full_path = os.path.join(SPRITES_DIR, sprite_path)
    
    if not os.path.exists(full_path):
        logger.warning(f"Sprite file not found: {full_path}")
        return None
    
    try:
        # Load image
        img = Image.open(full_path)
        
        # Convert to RGB if needed (handles RGBA, P mode, etc.)
        if img.mode != 'RGB':
            # Create a white background for transparency
            rgb_img = Image.new('RGB', img.size, (0, 0, 0))  # Black background
            if img.mode == 'RGBA':
                rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            else:
                rgb_img.paste(img)
            img = rgb_img
        
        # Resize to 16x16 if needed (Stardew Valley sprites should already be 16x16)
        if img.size != (16, 16):
            logger.debug(f"Resizing sprite from {img.size} to (16, 16)")
            img = img.resize((16, 16), Image.NEAREST)  # Use nearest neighbor to preserve pixel art
        
        # Convert to 2D array of RGB tuples
        pixels = img.load()
        sprite_data = []
        for y in range(16):
            row = []
            for x in range(16):
                pixel = pixels[x, y]
                # PIL returns RGB tuple
                row.append(pixel)
            sprite_data.append(row)
        
        logger.debug(f"Loaded sprite from {full_path}: {img.size}, mode={img.mode}")
        return sprite_data
        
    except Exception as e:
        logger.error(f"Failed to load sprite from {full_path}: {e}")
        return None


def get_pixel_art_image(image_key: str) -> Optional[List[List[Tuple[int, int, int]]]]:
    """
    Get pixel art image data by key, randomly selecting from available sprites.
    
    Parameters:
        image_key: Key for the image (e.g., "cow", "pig", "chicken")
        
    Returns:
        list: 2D array of RGB tuples, or None if key not found or file missing
    """
    # Get all sprites for this animal type
    animal_dir = Path(SPRITES_DIR) / image_key
    if not animal_dir.exists():
        logger.warning(f"No sprite directory found for image key: {image_key}")
        return None
    
    # Find all PNG files in the animal directory
    sprite_files = list(animal_dir.glob("*.png"))
    if not sprite_files:
        logger.warning(f"No sprite files found for image key: {image_key}")
        return None
    
    # Randomly select one sprite
    selected_sprite = random.choice(sprite_files)
    logger.debug(f"Selected sprite for {image_key}: {selected_sprite.name}")
    
    return _load_sprite_image(str(selected_sprite))


def get_all_image_keys():
    """Get all available image keys (animal types with sprites)."""
    animal_dir = Path(SPRITES_DIR)
    if not animal_dir.exists():
        return []
    
    # Return all subdirectories that contain PNG files
    image_keys = []
    for subdir in animal_dir.iterdir():
        if subdir.is_dir() and list(subdir.glob("*.png")):
            image_keys.append(subdir.name)
    
    return image_keys


def set_sprites_directory(path: str) -> None:
    """
    Set custom directory for Stardew Valley sprites.
    
    Parameters:
        path: Path to directory containing sprite files
    """
    global SPRITES_DIR
    SPRITES_DIR = path
    logger.info(f"Sprite directory set to: {SPRITES_DIR}")
