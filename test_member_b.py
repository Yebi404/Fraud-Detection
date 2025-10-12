#!/usr/bin/env python3
"""
Quick test script for Member B's ML Anomaly Detection
"""
import sys
import os

print("=" * 70)
print("Testing Member B's ML Anomaly Detection System")
print("=" * 70)
print()

# Test 1: Import check
print("Test 1: Checking imports...")
try:
    from agents.anomaly_detector import AnomalyDetector
    import scripts.run_detection as rd
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Test AnomalyDetector with sample data
print("Test 2: Testing AnomalyDetector with sample data...")
try:
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    sample_data = pd.DataFrame({
        'idx': range(n_samples),
        'step': np.random.randint(1, 100, n_samples),
        'type': np.random.choice(['TRANSFER', 'CASH_OUT', 'PAYMENT'], n_samples),
        'amount': np.random.uniform(100, 10000, n_samples),
        'nameOrig': [f'C{i}' for i in range(n_samples)],
        'nameDest': [f'M{i % 20}' for i in range(n_samples)],
        'isFraud': np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    })
    
    # Initialize detector
    detector = AnomalyDetector(sample_data, target_column="isFraud", svm_sample_size=50)
    print("✅ AnomalyDetector initialized successfully!")
    
    # Fit models
    print("   Training unsupervised models...")
    detector.fit()
    print("✅ Isolation Forest and SVM trained!")
    
    # Train XGBoost
    print("   Training supervised model (XGBoost)...")
    detector.train_xgboost()
    print("✅ XGBoost trained!")
    
    # Generate predictions
    print("   Generating predictions...")
    results = detector.predict()
    print(f"✅ Generated predictions for {len(results)} transactions!")
    
    # Check results format
    if len(results) > 0 and 'anomaly_score' in results[0]:
        print(f"   Sample anomaly score: {results[0]['anomaly_score']:.4f}")
    
except Exception as e:
    print(f"❌ AnomalyDetector test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Test CSV export
print("Test 3: Testing CSV export functionality...")
try:
    os.makedirs("models", exist_ok=True)
    
    detector.export_ml_scores_csv(
        out_path="models/test_ml_scores.csv",
        include_supervised=True
    )
    
    # Check if file was created
    if os.path.exists("models/test_ml_scores.csv"):
        print("✅ ML scores CSV exported successfully!")
        df = pd.read_csv("models/test_ml_scores.csv")
        print(f"   Exported {len(df)} rows with columns: {list(df.columns)}")
    else:
        print("❌ CSV file was not created")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ CSV export failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Test Member B's API
print("Test 4: Testing Member B's API endpoint...")
try:
    # Check if memberB_api.py can be imported
    import scripts.memberB_api as mb_api
    print("✅ Member B API module loaded successfully!")
    
    # Test with TestClient
    from fastapi.testclient import TestClient
    
    # Create test client
    client = TestClient(mb_api.app)
    
    # Create sample data file
    sample_data.to_csv("models/test_input.csv", index=False)
    
    # Test the /run-agentB endpoint
    response = client.post(
        "/run-agentB",
        json={"file_path": "models/test_input.csv"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            print("✅ /run-agentB endpoint works!")
            print(f"   API returned success status")
        else:
            print(f"❌ API returned error: {result}")
            sys.exit(1)
    else:
        print(f"❌ /run-agentB endpoint failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Member B API test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL MEMBER B TESTS PASSED!")
print("=" * 70)
print()
print("Member B's ML Anomaly Detection system is working correctly!")
print()
print("You can now:")
print("  1. Run detection: python scripts/run_detection.py")
print("  2. Start Member B API: python scripts/memberB_api.py")
print("  3. Use unified API: uvicorn api.unified_app:app --reload --port 8001")
print()

# Cleanup test files
if os.path.exists("models/test_ml_scores.csv"):
    os.remove("models/test_ml_scores.csv")
if os.path.exists("models/test_input.csv"):
    os.remove("models/test_input.csv")

