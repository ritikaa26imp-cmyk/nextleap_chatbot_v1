"""
Script to build knowledge base from scraped course data
Creates chunks, generates embeddings, and stores in vector database
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processor.chunker import CourseChunker
from src.embeddings.embedder import EmbeddingGenerator
from src.embeddings.vector_db import VectorDB


def main():
    """Build knowledge base from processed course data"""
    
    # Load processed course data
    processed_file = Path(__file__).parent.parent / "data" / "processed" / "nextleap_courses.json"
    
    if not processed_file.exists():
        print(f"Error: Processed data file not found: {processed_file}")
        print("Please run scrape_data.py first to generate course data.")
        return
    
    print("Loading course data...")
    with open(processed_file, 'r', encoding='utf-8') as f:
        courses_data = json.load(f)
    
    print(f"Loaded {len(courses_data)} courses")
    
    # Step 1: Chunk the data
    print("\nStep 1: Chunking course data...")
    chunker = CourseChunker()
    chunks = chunker.chunk_all_courses(courses_data)
    print(f"Created {len(chunks)} chunks")
    
    # Step 2: Generate embeddings
    print("\nStep 2: Generating embeddings...")
    # Set cache directories to /tmp to avoid including in Docker image
    import os
    os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
    os.environ['HF_HOME'] = '/tmp/huggingface'
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'
    embedder = EmbeddingGenerator()
    chunk_texts = [chunk["content"] for chunk in chunks]
    embeddings = embedder.generate_embeddings(chunk_texts)
    print(f"Generated {len(embeddings)} embeddings")
    
    # Step 3: Store in vector database
    print("\nStep 3: Storing in vector database...")
    vector_db = VectorDB()
    vector_db.add_chunks(chunks, embeddings)
    
    # Print summary
    info = vector_db.get_collection_info()
    print("\n" + "="*50)
    print("KNOWLEDGE BASE CREATED SUCCESSFULLY")
    print("="*50)
    print(f"Collection: {info['collection_name']}")
    print(f"Total chunks: {info['chunk_count']}")
    print(f"Database location: {vector_db.db_path}")
    print("\nKnowledge base is ready for queries!")


if __name__ == "__main__":
    main()

