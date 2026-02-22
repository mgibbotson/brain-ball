"""
Model loader: load artifact from config path/version (FR-008).
First release: no-op or static map; supports config-driven path for later.
"""
import logging
import os

logger = logging.getLogger(__name__)


def load_model(model_path: str | None = None, model_version: str | None = None):
    """
    Load model from path/version. First release: returns None (use stub in inference).
    Later: load from path or Kubeflow artifact store.
    """
    path = model_path or os.environ.get("MODEL_PATH")
    version = model_version or os.environ.get("MODEL_VERSION")
    if path or version:
        logger.info("Model path=%s version=%s (loading not implemented for first release)", path, version)
    return None
