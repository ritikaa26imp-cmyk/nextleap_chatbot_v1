"""
Script to run both backend and frontend servers
"""
import subprocess
import sys
import time
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_backend():
    """Run the FastAPI backend server"""
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "scripts/run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return backend_process

def run_frontend():
    """Run the frontend HTTP server"""
    print("Starting frontend server...")
    frontend_process = subprocess.Popen(
        [sys.executable, "scripts/run_frontend.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return frontend_process

if __name__ == "__main__":
    print("="*60)
    print("Starting Nextleap Chatbot - Backend & Frontend")
    print("="*60)
    print()
    
    # Start backend
    backend = run_backend()
    time.sleep(3)  # Wait for backend to start
    
    # Start frontend
    frontend = run_frontend()
    time.sleep(2)  # Wait for frontend to start
    
    print()
    print("="*60)
    print("✅ Servers are running!")
    print("="*60)
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:3000")
    print("API Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop both servers")
    print("="*60)
    
    try:
        # Wait for both processes
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Servers stopped.")
