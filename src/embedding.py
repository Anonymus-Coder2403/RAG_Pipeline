"""
Embedding Generation Module

This module handles generating embeddings for text using SentenceTransformers.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """Handles document embedding generation using SentenceTransformer"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager

        Args:
            model_name: HuggingFace model name for sentence embeddings
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model"""
        import logging
        import torch
        logger = logging.getLogger(__name__)
        try:
            # Check GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading embedding model: {self.model_name}")
            logger.info(f"Using device: {device}")

            if device == "cuda":
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"GPU: {gpu_name} ({gpu_memory:.1f} GB)")

            # Load model to specified device
            self.model = SentenceTransformer(self.model_name, device=device)
            embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}", exc_info=True)
            raise

    def generate_embeddings(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed
            show_progress: Whether to show progress bar

        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        import logging
        logger = logging.getLogger(__name__)

        if not self.model:
            raise ValueError("Model not loaded")

        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=show_progress)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model

        Returns:
            Embedding dimension
        """
        if not self.model:
            raise ValueError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()
