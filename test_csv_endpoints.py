#!/usr/bin/env python3
"""
Test script for the new CSV data endpoints for Member B
"""
import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response keys: {list(result.keys())}")
            
            # Show some sample data if it exists
            if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
                print(f"Sample record: {json.dumps(result['data'][0], indent=2)}")
            elif "results" in result and isinstance(result["results"], list) and len(result["results"]) > 0:
                print(f"Sample result: {json.dumps(result['results'][0], indent=2)}")
            else:
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on port 8001")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Run all endpoint tests"""
    print("Testing Member B CSV Data Endpoints")
    print("Make sure the API server is running: python api/unified_app.py")
    
    # Test 1: Get CSV data info (lightweight)
    test_endpoint("/v1/ml/data/info")
    
    # Test 2: Get chunk information
    test_endpoint("/v1/ml/data/chunks?chunk_size=1000")
    
    # Test 3: Get a small sample of CSV data
    test_endpoint("/v1/ml/data/sample?limit=5")
    
    # Test 4: Get first chunk of data (paginated)
    test_endpoint("/v1/ml/data?limit=1000&offset=0")
    
    # Test 5: Get second chunk of data
    test_endpoint("/v1/ml/data?limit=1000&offset=1000")
    
    # Test 6: Get all 10,000 records at once
    print("\n" + "="*60)
    print("Testing full dataset access (10,000 records)...")
    print("="*60)
    test_endpoint("/v1/ml/data?limit=10000")
    
    # Test 7: Run ML detection on CSV data (this might take a while)
    print("\n" + "="*60)
    print("Testing ML detection on CSV data (this may take a moment)...")
    print("="*60)
    test_endpoint("/v1/ml/detect-from-csv", method="POST")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
