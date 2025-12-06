"""
Vercel serverless function wrapper for FastAPI
This file handles all API routes for Vercel deployment
"""
import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for model caching (Vercel uses /tmp)
os.environ.setdefault('TRANSFORMERS_CACHE', '/tmp/transformers_cache')
os.environ.setdefault('HF_HOME', '/tmp/huggingface')
os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', '/tmp/sentence_transformers')

# Import the FastAPI app
from src.api.server import app

# Vercel expects a handler function - this is the entry point
def handler(request):
    """
    Vercel serverless function handler
    This wraps the FastAPI ASGI app for Vercel
    """
    from mangum import Mangum
    
    # Create Mangum adapter to convert ASGI app to AWS Lambda handler
    asgi_handler = Mangum(app, lifespan="off")
    
    # Convert Vercel request to ASGI scope
    return asgi_handler(request)

# Export handler for Vercel
__all__ = ['handler']

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
