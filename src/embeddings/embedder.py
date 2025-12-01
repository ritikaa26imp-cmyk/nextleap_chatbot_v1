"""
Embedding generator for course data chunks
"""
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """Generate embeddings for text chunks"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: Name of the sentence transformer model
        """
        try:
            print(f"Loading embedding model: {model_name}...")
            # Use device='cpu' explicitly to avoid CUDA issues on Railway
            # Cache models in a writable location (Railway's ephemeral storage)
            import os
            cache_dir = os.getenv('TRANSFORMERS_CACHE', '/tmp/transformers_cache')
            os.makedirs(cache_dir, exist_ok=True)
            self.model = SentenceTransformer(model_name, device='cpu', cache_folder=cache_dir)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

