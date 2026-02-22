"""
Text-to-animal inference. Stub mapping or config-driven model (first release).
"""
import logging
import os

logger = logging.getLogger(__name__)

# Stub mapping for first release; can be replaced by model_loader in T019
DEFAULT_STUB_MAP = {
    "beak": "bird",
    "fur": "dog",
    "tail": "dog",
    "woof": "dog",
    "meow": "cat",
    "feathers": "bird",
    "wings": "bird",
}


def get_animal(text: str) -> tuple[str, float]:
    """Return (animal, confidence) for the given text."""
    if not text or not isinstance(text, str):
        return "bird", 0.0
    t = text.strip().lower()
    if not t:
        return "bird", 0.0
    animal = DEFAULT_STUB_MAP.get(t, "bird")
    return animal, 1.0
