"""
Script to initialize knowledge base on Railway
This ensures the KB is built before the server starts
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.build_kb import main

if __name__ == "__main__":
    print("Building knowledge base for Railway deployment...")
    try:
        main()
        print("✅ Knowledge base built successfully!")
    except Exception as e:
        print(f"❌ Error building knowledge base: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

