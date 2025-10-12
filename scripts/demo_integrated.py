#!/usr/bin/env python3
"""
Demo Script: Integrated Fraud Detection (Members A & B)
========================================================

This script demonstrates how Member A and Member B's work integrate together.

Usage:
    python scripts/demo_integrated.py

Features:
    1. Runs Member B's ML anomaly detection
    2. Calls Member A's graph analysis API
    3. Merges results and displays integrated output
    4. Generates visualization-ready data
"""

import os
import sys
import json
import time
import pandas as pd
import requests
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("=" * 70)
print("🚀 INTEGRATED FRAUD DETECTION DEMO (Members A & B)")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Member B - ML Anomaly Detection
# ============================================================================
print("📊 STEP 1: Running Member B's ML Anomaly Detection...")
print("-" * 70)

try:
    from agents.anomaly_detector import AnomalyDetector
    
    # Check if data file exists
    DATA_PATH = "data/base_txns_full_for_ml.csv"
    
    if not os.path.exists(DATA_PATH):
        print(f"⚠️  Data file not found: {DATA_PATH}")
        print("   Please place your transaction data CSV in the data/ folder")
        print("   Expected columns: idx, step, type, amount, nameOrig, nameDest, isFraud")
        print()
        print("   For demo purposes, creating sample data...")
        
        # Create sample data
        os.makedirs("data", exist_ok=True)
        sample_data = pd.DataFrame({
            'idx': range(100),
            'step': [1] * 100,
            'type': ['TRANSFER'] * 50 + ['CASH_OUT'] * 50,
            'amount': [1000 + i * 10 for i in range(100)],
            'nameOrig': [f'C{i}' for i in range(100)],
            'nameDest': [f'M{i % 10}' for i in range(100)],
            'isFraud': [0] * 90 + [1] * 10
        })
        sample_data.to_csv(DATA_PATH, index=False)
        print(f"   ✅ Created sample data: {DATA_PATH}")
        print()
    
    # Load and process data
    data = pd.read_csv(DATA_PATH)
    print(f"   ✅ Loaded data: {data.shape[0]} transactions, {data.shape[1]} features")
    
    # Initialize and train models
    print("   🔧 Training ML models...")
    detector = AnomalyDetector(data, target_column="isFraud", svm_sample_size=10000)
    detector.fit()
    detector.train_xgboost()
    
    # Generate predictions
    print("   🎯 Generating anomaly scores...")
    results_ml = detector.predict()
    results_ml = detector.add_risk_scores(results_ml)
    
    # Save outputs
    os.makedirs("models", exist_ok=True)
    JSON_OUT = "models/anomaly_output_standard.json"
    CSV_OUT = "models/ml_scores.csv"
    
    with open(JSON_OUT, "w") as f:
        json.dump(results_ml, f, indent=4)
    
    detector.export_ml_scores_csv(out_path=CSV_OUT, include_supervised=True)
    
    print(f"   ✅ Member B outputs saved:")
    print(f"      - {JSON_OUT}")
    print(f"      - {CSV_OUT}")
    print()
    
    memberB_success = True
    
except Exception as e:
    print(f"   ❌ Error in Member B's detection: {str(e)}")
    print(f"      Continuing with graph analysis only...")
    print()
    memberB_success = False

# ============================================================================
# STEP 2: Member A - Graph Analysis (via API or direct)
# ============================================================================
print("🕸️  STEP 2: Running Member A's Graph Analysis...")
print("-" * 70)

try:
    # Check if API is running
    API_URL = "http://127.0.0.1:8001"
    api_running = False
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            api_running = True
            print(f"   ✅ API is running at {API_URL}")
    except:
        print(f"   ℹ️  API not running - using direct method")
    
    # Load transaction data
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        
        # Prepare transactions for API
        transactions = df.head(50).to_dict(orient='records')
        
        if api_running:
            # Use API
            print("   📡 Calling graph scoring API...")
            response = requests.post(
                f"{API_URL}/v1/graph/score",
                json={"transactions": transactions},
                timeout=30
            )
            
            if response.status_code == 200:
                results_graph = response.json()
                print(f"   ✅ Graph analysis complete: {results_graph['count']} scores")
            else:
                print(f"   ❌ API error: {response.status_code}")
                results_graph = None
        else:
            # Use direct method
            print("   🔧 Running graph scoring directly...")
            from src.graph_scoring import score_batch
            
            df_filtered = df[df["type"].isin(["TRANSFER","CASH_OUT"])].copy()
            results_list = score_batch(df_filtered)
            results_graph = {"count": len(results_list), "results": results_list}
            print(f"   ✅ Graph analysis complete: {results_graph['count']} scores")
        
        # Save graph results
        os.makedirs("outputs", exist_ok=True)
        GRAPH_OUT = "outputs/graph_scores.json"
        with open(GRAPH_OUT, "w") as f:
            json.dump(results_graph, f, indent=4)
        print(f"   ✅ Graph results saved: {GRAPH_OUT}")
        print()
        
        memberA_success = True
    else:
        print(f"   ⚠️  No data file found for graph analysis")
        memberA_success = False
        results_graph = None
        
except Exception as e:
    print(f"   ❌ Error in Member A's analysis: {str(e)}")
    print()
    memberA_success = False
    results_graph = None

# ============================================================================
# STEP 3: Integration - Merge Results
# ============================================================================
print("🔗 STEP 3: Integrating Results...")
print("-" * 70)

try:
    if memberB_success and memberA_success and results_graph:
        # Load ML scores
        ml_df = pd.read_csv(CSV_OUT)
        print(f"   📊 Member B results: {len(ml_df)} rows")
        
        # Load graph scores
        graph_df = pd.DataFrame(results_graph["results"])
        print(f"   📊 Member A results: {len(graph_df)} rows")
        
        # Merge on idx
        merged_df = pd.merge(ml_df, graph_df, on="idx", how="outer")
        print(f"   ✅ Merged results: {len(merged_df)} rows")
        
        # Display sample
        print()
        print("   📋 Sample Integrated Results (first 5 rows):")
        print("-" * 70)
        
        display_cols = ['idx', 'ml_score', 'ring_score_7d', 'amount', 'type']
        available_cols = [c for c in display_cols if c in merged_df.columns]
        print(merged_df[available_cols].head().to_string(index=False))
        print()
        
        # Save integrated results
        INTEGRATED_OUT = "outputs/integrated_results.csv"
        merged_df.to_csv(INTEGRATED_OUT, index=False)
        print(f"   ✅ Integrated results saved: {INTEGRATED_OUT}")
        print()
        
        # Generate summary statistics
        print("   📈 Summary Statistics:")
        print("-" * 70)
        if 'ml_score' in merged_df.columns:
            print(f"   ML Score Range: {merged_df['ml_score'].min():.4f} - {merged_df['ml_score'].max():.4f}")
        if 'ring_score_7d' in merged_df.columns:
            print(f"   Ring Score Range: {merged_df['ring_score_7d'].min():.4f} - {merged_df['ring_score_7d'].max():.4f}")
        
        # Flag high-risk transactions
        if 'ml_score' in merged_df.columns and 'ring_score_7d' in merged_df.columns:
            high_risk = merged_df[
                (merged_df['ml_score'] > merged_df['ml_score'].quantile(0.9)) |
                (merged_df['ring_score_7d'] > merged_df['ring_score_7d'].quantile(0.9))
            ]
            print(f"   🚨 High-risk transactions: {len(high_risk)} ({len(high_risk)/len(merged_df)*100:.1f}%)")
        print()
        
    elif memberB_success and not memberA_success:
        print("   ℹ️  Only Member B results available")
    elif memberA_success and not memberB_success:
        print("   ℹ️  Only Member A results available")
    else:
        print("   ⚠️  No results to integrate")
        
except Exception as e:
    print(f"   ❌ Error integrating results: {str(e)}")
    print()

# ============================================================================
# Final Summary
# ============================================================================
print()
print("=" * 70)
print("✅ DEMO COMPLETE!")
print("=" * 70)
print()
print("📁 Generated Files:")
print("-" * 70)

output_files = [
    ("models/anomaly_output_standard.json", "Member B: ML detection results (JSON)"),
    ("models/ml_scores.csv", "Member B: ML scores (CSV)"),
    ("outputs/graph_scores.json", "Member A: Graph analysis results"),
    ("outputs/integrated_results.csv", "Integrated: Combined A+B results"),
]

for filepath, description in output_files:
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✅ {filepath}")
        print(f"      {description} ({size:,} bytes)")
    else:
        print(f"   ⚠️  {filepath} (not generated)")

print()
print("🎯 Next Steps:")
print("-" * 70)
print("   1. Review integrated results in: outputs/integrated_results.csv")
print("   2. Pass results to Member C (Verifier Agent)")
print("   3. Display in Member D's UI/Dashboard")
print()
print("💡 To run the unified API:")
print("   uvicorn api.unified_app:app --reload --port 8001")
print()
print("📚 Documentation:")
print("   - README.md: Full project documentation")
print("   - docs/api.md: API reference")
print("   - TEAM_HANDOFF.md: Integration guide")
print()
print("=" * 70)


