"""
FastAPI server for Nextleap FAQ chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
import os


# Initialize FastAPI app
app = FastAPI(
    title="Nextleap FAQ Chatbot API",
    description="API for answering questions about Nextleap courses",
    version="1.0.0"
)

# CORS middleware - Allow frontend to access API
# Since we're serving frontend from the same origin, CORS is less critical
# But keep it for API-only access if needed
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


def get_query_handler():
    """Initialize and return query handler (singleton pattern)"""
    global _vector_db, _embedder, _llm_handler, _query_handler, _conversation_memory
    
    if _query_handler is None:
        print("Initializing components...")
        
        # Initialize vector DB and embedder
        _vector_db = VectorDB()
        _embedder = EmbeddingGenerator()
        
        # Initialize Gemini LLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        _llm_handler = GeminiLLMHandler(api_key=api_key)
        
        # Initialize conversation memory
        _conversation_memory = ConversationMemory(max_messages=20)
        
        # Initialize query handler with memory
        _query_handler = QueryHandler(_vector_db, _embedder, _llm_handler, _conversation_memory)
        
        print("Components initialized successfully!")
    
    return _query_handler


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"  # Add session_id for conversation memory


class QueryResponse(BaseModel):
    answer: str
    source_url: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    knowledge_base_chunks: int


# Serve frontend static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # Mount static files (CSS, JS) - but we'll serve them manually for better control
    # app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    # Serve index.html for root
    @app.get("/")
    async def root():
        """Serve the frontend index.html"""
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        # Fallback to health check if frontend not found
        try:
            vector_db = VectorDB()
            info = vector_db.get_collection_info()
            return {
                "status": "healthy",
                "message": "Nextleap FAQ Chatbot API is running (frontend not found)",
                "knowledge_base_chunks": info["chunk_count"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "knowledge_base_chunks": 0
            }
    
    # Serve static files (CSS, JS)
    @app.get("/{filename}")
    async def serve_static(filename: str):
        """Serve static files (CSS, JS)"""
        # Don't serve API routes as static files
        if filename in ["docs", "openapi.json", "health", "query"] or filename.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        static_file = frontend_path / filename
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # For SPA routing, serve index.html for unknown routes
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Not found")
else:
    # If frontend not found, provide health check
    @app.get("/")
    async def root():
        """Health check endpoint (frontend not available)"""
        try:
            vector_db = VectorDB()
            info = vector_db.get_collection_info()
            return {
                "status": "healthy",
                "message": "Nextleap FAQ Chatbot API is running",
                "knowledge_base_chunks": info["chunk_count"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "knowledge_base_chunks": 0
            }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return await root()


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
        # Pass session_id to maintain conversation context
        result = handler.answer_query(request.question, session_id=request.session_id)
        
        return QueryResponse(
            answer=result["answer"],
            source_url=result.get("source_url")
        )
    except Exception as e:
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


# Serve frontend static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # Mount static files (CSS, JS)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    # Serve index.html for root and all other routes (SPA routing)
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html"""
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend not found"}
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve frontend for all routes (SPA)"""
        # Check if it's an API route
        if path.startswith(("api/", "docs", "openapi.json", "health", "query")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for frontend routes
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Frontend not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

