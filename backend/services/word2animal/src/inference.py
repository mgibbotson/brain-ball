"""
Text-to-animal inference using sentence-transformers (same logic as client image_embeddings).
Maps input text to an animal key via embedding cosine similarity.
"""
import logging
import os
import time
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Same lightweight model as client (good for Pi / small containers)
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_THRESHOLD = 0.4

# Animal keys and labels (must match client pixel_art / display expectations)
ANIMAL_LABELS: Dict[str, List[str]] = {
    "cow": ["cow", "cattle", "bovine", "moo", "mooing"],
    "pig": ["pig", "swine", "hog", "oink", "oinking", "snort"],
    "chicken": ["chicken", "hen", "rooster", "cluck", "clucking", "bawk"],
    "sheep": ["sheep", "lamb", "ewe", "ram", "baa", "baaing", "bleat"],
    "horse": ["horse", "pony", "mare", "stallion", "neigh", "whinny"],
    "duck": ["duck", "drake", "quack", "quacking"],
    "goat": ["goat", "kid", "bleat", "bleating"],
    "dog": ["dog", "puppy", "pup", "woof", "bark", "barking"],
    "cat": ["cat", "kitten", "kitty", "meow", "meowing", "purr"],
}

_model = None
_embeddings: Dict[str, object] = {}  # animal -> numpy vector
_initialized = False


def _ensure_model():
    global _model, _embeddings, _initialized
    if _initialized:
        return
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError(
            "sentence-transformers not available. Install with: pip install sentence-transformers"
        )
    model_name = os.environ.get("WORD2ANIMAL_MODEL", DEFAULT_MODEL_NAME)
    threshold = float(os.environ.get("WORD2ANIMAL_THRESHOLD", DEFAULT_THRESHOLD))
    logger.info("Loading embedding model: %s (threshold=%.2f)", model_name, threshold)
    start = time.time()
    try:
        _model = SentenceTransformer(model_name, local_files_only=True)
        logger.info("Loaded model from local cache in %.2fs", time.time() - start)
    except (OSError, ValueError, FileNotFoundError):
        logger.info("Model not in cache, downloading from HuggingFace (first time only)...")
        _model = SentenceTransformer(model_name)
        logger.info("Model downloaded and cached in %.2fs", time.time() - start)
    for animal, labels in ANIMAL_LABELS.items():
        primary = labels[0]
        emb = _model.encode(primary, convert_to_numpy=True, show_progress_bar=False)
        _embeddings[animal] = emb
    _initialized = True
    logger.info("Animal embeddings initialized (%d animals)", len(_embeddings))


def _cosine_similarity(vec1: object, vec2: object) -> float:
    import numpy as np
    dot = float(np.dot(vec1, vec2))
    n1 = np.linalg.norm(vec1)
    n2 = np.linalg.norm(vec2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (float(n1) * float(n2))


def get_animal(text: str) -> Tuple[str, float]:
    """
    Return (animal, confidence) for the given text using embedding similarity.
    Confidence is the cosine similarity (0–1); default "bird" with 0.0 when no match.
    """
    if not text or not isinstance(text, str):
        return "bird", 0.0
    t = text.strip()
    if not t:
        return "bird", 0.0
    _ensure_model()
    word_emb = _model.encode(t, convert_to_numpy=True, show_progress_bar=False)
    threshold = float(os.environ.get("WORD2ANIMAL_THRESHOLD", DEFAULT_THRESHOLD))
    best_match = None
    best_sim = -1.0
    for animal, image_emb in _embeddings.items():
        sim = _cosine_similarity(word_emb, image_emb)
        if sim > best_sim and sim >= threshold:
            best_sim = sim
            best_match = animal
    if best_match:
        logger.debug("Matched %r -> %s (similarity=%.3f)", t, best_match, best_sim)
        return best_match, float(min(1.0, max(0.0, best_sim)))
    logger.debug("No match for %r (best=%.3f, threshold=%.2f)", t, best_sim, threshold)
    return "bird", 0.0
