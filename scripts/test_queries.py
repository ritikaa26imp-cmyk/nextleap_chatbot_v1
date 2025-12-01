"""
Test script to run 5 different queries against the backend
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

test_queries = [
    "When is the product manager fellowship starting?",
    "What is the cost of the data analyst course?",
    "Who are the instructors for product management course?",
    "What is the curriculum for UI UX design course?",
    "Tell me about placements for business analyst course"
]

def test_query(question: str):
    """Test a single query"""
    print(f"\n{'='*70}")
    print(f"Query: {question}")
    print('='*70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"\nAnswer:")
        print(f"  {result['answer']}")
        print(f"\nSource URL: {result.get('source_url', 'N/A')}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING NEXTLEAP FAQ CHATBOT BACKEND")
    print("="*70)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Server not responding. Make sure it's running on port 8000")
        exit(1)
    
    # Test all queries
    print(f"\nTesting {len(test_queries)} queries...")
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}]")
        success = test_query(query)
        results.append(success)
        time.sleep(1)  # Small delay between queries
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total queries: {len(test_queries)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print("="*70)


