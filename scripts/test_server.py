"""
Test script for the FastAPI server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_query_post(question: str):
    """Test query endpoint (POST)"""
    print(f"Testing POST /query with question: '{question}'")
    response = requests.post(
        f"{BASE_URL}/query",
        json={"question": question}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_query_get(question: str):
    """Test query endpoint (GET)"""
    print(f"Testing GET /query with question: '{question}'")
    response = requests.get(
        f"{BASE_URL}/query",
        params={"question": question}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("="*50)
    print("Testing Nextleap FAQ Chatbot API")
    print("="*50)
    print()
    
    # Test health
    test_health()
    
    # Test queries
    test_queries = [
        "Tell me price and date of Nextleap data analysis cohort",
        "What is the cost of the data analyst course?",
        "Who are the instructors for product management course?"
    ]
    
    for query in test_queries:
        test_query_post(query)
        print("-"*50)
        print()


