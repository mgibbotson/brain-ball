"""Image embedding system for vector distance matching."""

import logging
import os
from typing import Optional, Dict, List
import numpy as np

logger = logging.getLogger(__name__)

# Default embedding model (lightweight for Raspberry Pi Zero W)
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ImageEmbeddings:
    """Handles vector distance matching for word-to-image mapping."""
    
    def __init__(self, model_name: str = None, threshold: float = 0.5):
        """
        Initialize image embedding system.
        
        Parameters:
            model_name: Name of sentence-transformers model to use
                       (defaults to all-MiniLM-L6-v2 for lightweight operation)
            threshold: Minimum cosine similarity threshold for matching (0.0-1.0)
        """
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.threshold = threshold
        self._model = None
        self._image_embeddings: Dict[str, np.ndarray] = {}
        self._image_labels: Dict[str, List[str]] = {}
        self._initialized = False
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            import os
        except ImportError:
            raise RuntimeError(
                "sentence-transformers not available. Install with: pip install sentence-transformers"
            )
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Optimize loading: try local-only first, then fall back to online
            # This avoids unnecessary network requests if model is already cached
            import time
            start_time = time.time()
            
            try:
                # Try loading from local cache only (much faster - no network requests)
                # This will fail if model isn't cached yet
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
                load_time = time.time() - start_time
                logger.info(f"Loaded model from local cache in {load_time:.2f}s")
            except (OSError, ValueError, FileNotFoundError) as e:
                # Model not in cache, need to download (first time only)
                logger.info("Model not in local cache, downloading from HuggingFace (first time only)...")
                # Download and cache the model
                self._model = SentenceTransformer(self.model_name)
                load_time = time.time() - start_time
                logger.info(f"Model downloaded and cached in {load_time:.2f}s (future loads will be faster)")
            
            self._initialized = True
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    def register_image(self, image_key: str, labels: List[str]):
        """
        Register an image with its labels for embedding matching.
        
        Parameters:
            image_key: Key for the image (e.g., "cow", "pig")
            labels: List of label strings that should match this image
                   (e.g., ["cow", "cattle", "bovine", "moo"])
        """
        if not self._initialized:
            self._initialize_model()
        
        if not labels:
            raise ValueError("labels must be non-empty")
        
        # Store labels
        self._image_labels[image_key] = labels
        
        # Compute embedding for the primary label (first one)
        # For better matching, we could average embeddings of all labels
        primary_label = labels[0]
        embedding = self._model.encode(primary_label, convert_to_numpy=True, show_progress_bar=False)
        self._image_embeddings[image_key] = embedding
        
        logger.debug(f"Registered image '{image_key}' with labels: {labels}")
    
    def find_closest_image(self, word: str) -> Optional[str]:
        """
        Find closest image using vector distance matching.
        
        Parameters:
            word: Recognized word to match
            
        Returns:
            str: Image key of closest match, or None if no match above threshold
        """
        if not self._initialized:
            self._initialize_model()
        
        if not word:
            return None
        
        if not self._image_embeddings:
            logger.warning("No images registered for embedding matching")
            return None
        
        try:
            # Convert word to embedding
            word_embedding = self._model.encode(word, convert_to_numpy=True, show_progress_bar=False)
            
            # Compute cosine similarity with all image embeddings
            best_match = None
            best_similarity = -1.0
            
            for image_key, image_embedding in self._image_embeddings.items():
                # Compute cosine similarity
                similarity = self._cosine_similarity(word_embedding, image_embedding)
                
                if similarity > best_similarity and similarity >= self.threshold:
                    best_similarity = similarity
                    best_match = image_key
            
            if best_match:
                logger.debug(f"Matched '{word}' to '{best_match}' (similarity: {best_similarity:.3f})")
                return best_match
            else:
                logger.debug(f"No match found for '{word}' (best similarity: {best_similarity:.3f}, threshold: {self.threshold})")
                return None
                
        except Exception as e:
            logger.error(f"Failed to find closest image for '{word}': {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Parameters:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Cosine similarity (-1.0 to 1.0)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


def create_farm_animal_embeddings() -> ImageEmbeddings:
    """
    Create image embeddings for animals with their associated labels.
    
    Returns:
        ImageEmbeddings: Initialized embedding system with animals registered
    """
    embeddings = ImageEmbeddings(threshold=0.4)  # Lower threshold for better matching
    
    # Register animals with their labels
    # Each animal has multiple labels including their name and sounds
    embeddings.register_image("cow", ["cow", "cattle", "bovine", "moo", "mooing"])
    embeddings.register_image("pig", ["pig", "swine", "hog", "oink", "oinking", "snort"])
    embeddings.register_image("chicken", ["chicken", "hen", "rooster", "cluck", "clucking", "bawk"])
    embeddings.register_image("sheep", ["sheep", "lamb", "ewe", "ram", "baa", "baaing", "bleat"])
    embeddings.register_image("horse", ["horse", "pony", "mare", "stallion", "neigh", "whinny"])
    embeddings.register_image("duck", ["duck", "drake", "quack", "quacking"])
    embeddings.register_image("goat", ["goat", "kid", "bleat", "bleating"])
    embeddings.register_image("dog", ["dog", "puppy", "pup", "woof", "bark", "barking"])
    embeddings.register_image("cat", ["cat", "kitten", "kitty", "meow", "meowing", "purr"])
    
    logger.info("Animal embeddings initialized")
    return embeddings
