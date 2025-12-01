"""
FastAPI server for Nextleap FAQ chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.embeddings.embedder import EmbeddingGenerator
from src.embeddings.vector_db import VectorDB
from src.query.query_handler import QueryHandler
from src.query.llm_handler import GeminiLLMHandler
from src.query.conversation_memory import ConversationMemory


# Initialize FastAPI app
app = FastAPI(
    title="Nextleap FAQ Chatbot API",
    description="API for answering questions about Nextleap courses",
    version="1.0.0"
)

# CORS middleware - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for initialized components
_vector_db = None
_embedder = None
_llm_handler = None
_query_handler = None
_conversation_memory = None
_initialization_error = None


def get_query_handler():
    """Initialize and return query handler (singleton pattern)"""
    global _vector_db, _embedder, _llm_handler, _query_handler, _conversation_memory, _initialization_error
    
    if _query_handler is None:
        try:
            print("Initializing components...")
            
            # Initialize vector DB and embedder
            print("  - Initializing VectorDB...")
            _vector_db = VectorDB()
            print("  - Initializing EmbeddingGenerator...")
            _embedder = EmbeddingGenerator()
            
            # Initialize Gemini LLM
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
            
            print("  - Initializing Gemini LLM...")
            _llm_handler = GeminiLLMHandler(api_key=api_key)
            
            # Initialize conversation memory
            print("  - Initializing ConversationMemory...")
            _conversation_memory = ConversationMemory(max_messages=20)
            
            # Initialize query handler with memory
            print("  - Initializing QueryHandler...")
            _query_handler = QueryHandler(_vector_db, _embedder, _llm_handler, _conversation_memory)
            
            print("Components initialized successfully!")
            _initialization_error = None
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR during initialization: {error_msg}")
            import traceback
            traceback.print_exc()
            _initialization_error = error_msg
            raise
    
    return _query_handler


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"


class QueryResponse(BaseModel):
    answer: str
    source_url: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    knowledge_base_chunks: int


# API Endpoints - Define these BEFORE frontend routes
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint - lightweight, doesn't require full initialization"""
    try:
        # Try to get collection info, but don't fail if not initialized yet
        try:
            vector_db = VectorDB()
            info = vector_db.get_collection_info()
            chunk_count = info.get("chunk_count", 0)
        except Exception as e:
            print(f"Warning: Could not get collection info: {e}")
            chunk_count = 0
        
        # Check if there's an initialization error
        if _initialization_error:
            return {
                "status": "error",
                "message": f"Initialization error: {_initialization_error}",
                "knowledge_base_chunks": chunk_count
            }
        
        return {
            "status": "healthy",
            "message": "Nextleap FAQ Chatbot API is running",
            "knowledge_base_chunks": chunk_count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "knowledge_base_chunks": 0
        }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Answer a question about Nextleap courses
    
    Args:
        request: Query request with question and optional session_id
        
    Returns:
        Query response with answer and source URL
    """
    try:
        handler = get_query_handler()
        result = handler.answer_query(request.question, session_id=request.session_id)
        
        return QueryResponse(
            answer=result["answer"],
            source_url=result.get("source_url")
        )
    except ValueError as e:
        # Handle missing API key or initialization errors
        error_msg = str(e)
        print(f"Initialization error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Initialization error: {error_msg}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing query: {error_details}")
        # Don't expose full traceback to client, just the error message
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/query")
async def query_get(question: str):
    """
    Answer a question (GET endpoint for convenience)
    
    Args:
        question: User question
        
    Returns:
        Query response with answer and source URL
    """
    try:
        handler = get_query_handler()
        result = handler.answer_query(question)
        
        return QueryResponse(
            answer=result["answer"],
            source_url=result.get("source_url")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


# Serve frontend static files - Define AFTER API routes
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # Serve index.html for root
    @app.get("/")
    async def root():
        """Serve the frontend index.html"""
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        # Fallback to health check if frontend not found
        return await health()
    
    # Serve static files (CSS, JS) - catch-all for frontend routes
    @app.get("/{filename}")
    async def serve_static(filename: str):
        """Serve static files (CSS, JS) or SPA routes"""
        # Check if it's a static file
        static_file = frontend_path / filename
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # For SPA routing, serve index.html for unknown routes
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Not found")
else:
    # If frontend not found, provide health check at root
    @app.get("/")
    async def root():
        """Health check endpoint (frontend not available)"""
        return await health()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
