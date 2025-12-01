"""
Script to run the FastAPI server
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set API key from command line or environment
if len(sys.argv) > 1:
    api_key = sys.argv[1]
    os.environ["GEMINI_API_KEY"] = api_key
    print(f"Using API key from command line argument")
elif os.getenv("GEMINI_API_KEY"):
    print(f"Using API key from environment variable")
else:
    # API key must be set via environment variable
    print("ERROR: GEMINI_API_KEY environment variable is required!")
    print("Please set it using: export GEMINI_API_KEY='your_api_key_here'")
    print("Or create a .env file with: GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)

# Import and run server
from src.api.server import app
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting Nextleap FAQ Chatbot API Server")
    print("="*50)
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

