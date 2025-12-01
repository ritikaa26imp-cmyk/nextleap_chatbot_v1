"""
Simple API script for querying the knowledge base
Can be used as a backend service
Now uses Gemini 2.0 Flash for answer generation
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.embedder import EmbeddingGenerator
from src.embeddings.vector_db import VectorDB
from src.query.query_handler import QueryHandler
from src.query.llm_handler import GeminiLLMHandler


# Initialize components (singleton pattern)
_vector_db = None
_embedder = None
_llm_handler = None
_query_handler = None


def get_query_handler():
    """Get or create query handler instance with Gemini LLM"""
    global _vector_db, _embedder, _llm_handler, _query_handler
    
    if _query_handler is None:
        _vector_db = VectorDB()
        _embedder = EmbeddingGenerator()
        
        # Initialize Gemini LLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY environment variable is required!")
            print("Please set it using: export GEMINI_API_KEY='your_api_key_here'")
            sys.exit(1)
        _llm_handler = GeminiLLMHandler(api_key=api_key)
        
        _query_handler = QueryHandler(_vector_db, _embedder, _llm_handler)
    
    return _query_handler


def answer_question(question: str) -> dict:
    """
    Answer a question about Nextleap courses
    
    Args:
        question: User question
        
    Returns:
        Dictionary with answer and source_url
    """
    handler = get_query_handler()
    result = handler.answer_query(question)
    
    return {
        "answer": result["answer"],
        "source_url": result["source_url"]
    }


if __name__ == "__main__":
    """CLI interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python query_api.py '<your question>'")
        print("\nExample:")
        print("  python query_api.py 'Tell me price and date of Nextleap data analysis cohort'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    result = answer_question(question)
    
    print(f"\nQuestion: {question}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSource: {result['source_url']}")

