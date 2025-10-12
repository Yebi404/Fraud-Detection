#!/usr/bin/env python3
"""
Quick test script for Member A's API
"""
import sys
import json

print("=" * 70)
print("Testing Member A's Graph & Link Analysis API")
print("=" * 70)
print()

# Test 1: Import check
print("Test 1: Checking imports...")
try:
    from api.app import app
    from src.graph_scoring import score_batch, build_graph
    from src.precision_scoring import precision_for_txn
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Test graph scoring module
print("Test 2: Testing graph scoring module...")
try:
    import pandas as pd
    
    # Create sample data
    test_data = pd.DataFrame({
        'idx': [1, 2, 3],
        'step': [95, 96, 97],
        'type': ['TRANSFER', 'TRANSFER', 'CASH_OUT'],
        'amount': [1000, 2000, 1500],
        'nameOrig': ['U1', 'U2', 'U3'],
        'nameDest': ['R1', 'R1', 'R2']
    })
    
    # Test scoring
    results = score_batch(test_data)
    
    if len(results) > 0 and 'ring_score_7d' in results[0]:
        print(f"✅ Graph scoring works! Processed {len(results)} transactions")
        print(f"   Sample score: {results[0]['ring_score_7d']:.4f}")
    else:
        print("❌ Graph scoring returned unexpected format")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Graph scoring failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Test precision scoring module
print("Test 3: Testing precision scoring module...")
try:
    # Build graph from test data
    G = build_graph(test_data)
    
    # Test precision scoring
    result = precision_for_txn(G, "U1", "R1", 95)
    
    if 'ring_score_7d' in result and 'ring_score_30d' in result:
        print(f"✅ Precision scoring works!")
        print(f"   7d score: {result['ring_score_7d']:.4f}")
        print(f"   30d score: {result['ring_score_30d']:.4f}")
    else:
        print("❌ Precision scoring returned unexpected format")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Precision scoring failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Test FastAPI endpoints
print("Test 4: Testing FastAPI endpoints...")
try:
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    if response.status_code == 200 and response.json().get("status") == "ok":
        print("✅ /health endpoint works!")
    else:
        print(f"❌ /health endpoint failed: {response.status_code}")
        sys.exit(1)
    
    # Test graph score endpoint
    payload = {
        "transactions": [
            {"idx": 1, "step": 95, "type": "TRANSFER", "amount": 1000, "nameOrig": "U1", "nameDest": "R1"},
            {"idx": 2, "step": 96, "type": "TRANSFER", "amount": 2000, "nameOrig": "U2", "nameDest": "R1"},
        ]
    }
    
    response = client.post("/v1/graph/score", json=payload)
    if response.status_code == 200:
        result = response.json()
        if result["count"] == 2 and "ring_score_7d" in result["results"][0]:
            print(f"✅ /v1/graph/score endpoint works! Processed {result['count']} transactions")
        else:
            print(f"❌ /v1/graph/score returned unexpected format")
            sys.exit(1)
    else:
        print(f"❌ /v1/graph/score failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    # Test precision endpoint
    payload = {
        "transactions": [
            {"idx": 1, "step": 95, "type": "TRANSFER", "amount": 1000, "nameOrig": "U1", "nameDest": "R1"},
        ],
        "focus_idx": 1
    }
    
    response = client.post("/v1/graph/precision", json=payload)
    if response.status_code == 200:
        result = response.json()
        if "ring_score_7d" in result and "ring_score_30d" in result:
            print(f"✅ /v1/graph/precision endpoint works!")
        else:
            print(f"❌ /v1/graph/precision returned unexpected format")
            sys.exit(1)
    else:
        print(f"❌ /v1/graph/precision failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"❌ API endpoint test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL MEMBER A TESTS PASSED!")
print("=" * 70)
print()
print("Member A's Graph & Link Analysis API is working correctly!")
print()
print("You can now start the API with:")
print("  uvicorn api.app:app --reload --port 8001")
print()
print("Or test the unified API (both A & B):")
print("  uvicorn api.unified_app:app --reload --port 8001")
print()

