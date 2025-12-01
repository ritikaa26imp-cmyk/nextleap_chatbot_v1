"""
Test script to query the knowledge base
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.embedder import EmbeddingGenerator
from src.embeddings.vector_db import VectorDB
from src.query.query_handler import QueryHandler


def main():
    """Test query handler"""
    
    # Initialize components
    print("Initializing query handler...")
    vector_db = VectorDB()
    embedder = EmbeddingGenerator()
    query_handler = QueryHandler(vector_db, embedder)
    
    # Check if knowledge base exists
    info = vector_db.get_collection_info()
    if info["chunk_count"] == 0:
        print("Error: Knowledge base is empty!")
        print("Please run build_kb.py first to create the knowledge base.")
        return
    
    print(f"Knowledge base loaded: {info['chunk_count']} chunks available")
    
    # Test query
    test_query = "Tell me price and date of Nextleap data analysis cohort"
    print(f"\n{'='*50}")
    print(f"Query: {test_query}")
    print(f"{'='*50}\n")
    
    # Get answer
    result = query_handler.answer_query(test_query)
    
    # Display result
    print("Answer:")
    print(f"  {result['answer']}")
    print(f"\nSource URL: {result['source_url']}")
    print(f"Contexts used: {result['contexts_used']}")
    
    # Test a few more queries
    print("\n" + "="*50)
    print("Testing additional queries...")
    print("="*50)
    
    additional_queries = [
        "What is the cost of the data analyst course?",
        "When does the data analyst batch start?",
        "What is the curriculum for data analyst course?",
        "Who are the instructors for product management course?"
    ]
    
    for query in additional_queries:
        print(f"\nQuery: {query}")
        result = query_handler.answer_query(query)
        print(f"Answer: {result['answer']}")
        print(f"Source: {result['source_url']}")


if __name__ == "__main__":
    main()


