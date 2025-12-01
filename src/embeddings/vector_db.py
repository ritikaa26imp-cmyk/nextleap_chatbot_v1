"""
Vector database operations using ChromaDB
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path


class VectorDB:
    """Vector database for storing and retrieving course data"""
    
    def __init__(self, db_path: str = "data/knowledge_base/chroma_db", collection_name: str = "nextleap_courses"):
        """
        Initialize vector database
        
        Args:
            db_path: Path to store ChromaDB
            collection_name: Name of the collection
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        # Use get_or_create_collection which handles both cases
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Nextleap course data"}
        )
    
    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add chunks with embeddings to the database
        
        Args:
            chunks: List of chunk dictionaries with content and metadata
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Prepare data for ChromaDB
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {}).copy()
            # ChromaDB requires metadata values to be strings, numbers, or bools
            # Convert lists to strings
            for key, value in metadata.items():
                if isinstance(value, list):
                    metadata[key] = ", ".join(str(v) for v in value)
                elif value is None:
                    metadata[key] = ""
            
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Added {len(chunks)} chunks to vector database")
    
    def search(self, query_embedding: List[float], n_results: int = 5, filter_dict: Optional[Dict] = None) -> Dict:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            Dictionary with results
        """
        where = filter_dict if filter_dict else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection.name,
            "chunk_count": count
        }

