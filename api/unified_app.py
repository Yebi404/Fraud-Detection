# api/unified_app.py
"""
Unified Fraud Detection API
Integrates Member A (Graph Analysis) and Member B (ML Anomaly Detection)
"""
from typing import List, Any, Dict, Optional
import math
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import pandas as pd
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.graph_scoring import score_batch, build_graph
from src.precision_scoring import precision_for_txn
from agents.anomaly_detector import AnomalyDetector

app = FastAPI(
    title="Integrated Fraud Detection System (Members A & B)",
    version="2.0.0",
    description="Combined Graph & Link Analysis + ML Anomaly Detection service",
)

# ------------ Utils ------------

def _sanitize_for_json(obj: Any) -> Any:
    """Recursively replace NaN/Inf values with JSON-safe ones (None).
    - float NaN/Inf -> None
    - pandas/numpy NaNs -> None
    - lists/dicts -> sanitize elements
    """
    if obj is None:
        return None
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (str, bool)):
        return obj
    if isinstance(obj, list):
        return [_sanitize_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    # Fallback for pandas/numpy objects
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass
    return obj

# ------------ Models ------------

class Txn(BaseModel):
    idx: int = Field(..., description="Unique transaction id within batch")
    step: int
    type: str
    amount: float
    nameOrig: str
    nameDest: str
    isFraud: Optional[int] = Field(None, description="Label (optional)")

    @field_validator("type")
    @classmethod
    def norm_type(cls, v: str) -> str:
        return str(v).upper()

class ScoreRequest(BaseModel):
    transactions: List[Txn]

class ScoreResponse(BaseModel):
    count: int
    results: List[Dict[str, Any]]

class PrecisionRequest(BaseModel):
    transactions: List[Txn]
    focus_idx: int

class UnifiedRequest(BaseModel):
    """Request for unified scoring (both Member A and B)"""
    transactions: List[Txn]
    run_ml_detection: bool = Field(True, description="Run Member B's ML detection")
    run_graph_analysis: bool = Field(True, description="Run Member A's graph analysis")

class MLDetectionRequest(BaseModel):
    """Request for Member B's ML detection"""
    file_path: str = Field(..., description="Path to CSV file with transaction data")

# ------------ Member A Routes (Graph & Link Analysis) ------------

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Integrated Fraud Detection (Members A & B)",
        "version": "2.0.0"
    }

@app.post("/v1/graph/score", response_model=ScoreResponse, tags=["Member A: Graph Analysis"])
def graph_score(req: ScoreRequest):
    """
    Member A: FAST batch graph scoring
    Returns ring scores based on network analysis
    """
    df = pd.DataFrame([t.model_dump() for t in req.transactions])

    needed = ["idx","step","type","amount","nameOrig","nameDest"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        return {"count": 0, "results": [], "warning": f"Missing columns: {missing}"}

    df = df[df["type"].isin(["TRANSFER","CASH_OUT"])].copy()
    results = score_batch(df)
    return {"count": len(results), "results": results}

@app.post("/v1/graph/precision", tags=["Member A: Graph Analysis"])
def graph_precision(req: PrecisionRequest):
    """
    Member A: Detailed precision analysis for single transaction
    Compares 7-day vs 30-day subgraph features
    """
    df = pd.DataFrame([t.model_dump() for t in req.transactions])
    needed = ["idx","step","type","amount","nameOrig","nameDest"]
    for c in needed:
        if c not in df.columns:
            return {"error": f"Missing column {c} in transactions"}

    if req.focus_idx not in set(df["idx"].tolist()):
        return {"error": f"focus_idx {req.focus_idx} not found in provided transactions"}

    G = build_graph(df)
    row = df.loc[df["idx"] == req.focus_idx].iloc[0]
    res = precision_for_txn(G, str(row["nameOrig"]), str(row["nameDest"]), int(row["step"]))
    return {"focus_idx": int(req.focus_idx), **res}

# ------------ Member B Routes (ML Anomaly Detection) ------------

@app.get("/v1/ml/data", tags=["Member B: ML Anomaly Detection"])
def get_csv_data(limit: int = 1000, offset: int = 0):
    """
    Member B: Get CSV data from the data folder with pagination
    Returns the transaction data for ML analysis with pagination support
    
    Parameters:
    - limit: Maximum number of records to return (default: 1000, max: 10000)
    - offset: Number of records to skip (default: 0)
    """
    try:
        # Path to the CSV file in the data folder
        csv_path = os.path.join(project_root, "data", "base_txns_10k_ml_slim.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV data file not found")
        
        # Limit the maximum records to prevent API hanging
        limit = min(limit, 10000)  # Cap at 10000 records max (full dataset)
        
        # Read the CSV data with pagination
        data = pd.read_csv(csv_path, skiprows=range(1, offset + 1), nrows=limit)
        
        # Get total count without loading all data
        total_count = len(pd.read_csv(csv_path, usecols=[0]))  # Just count first column
        
        # Convert to JSON-safe format
        data_dict = data.to_dict(orient="records")
        
        return {
            "status": "success",
            "file_path": csv_path,
            "count": len(data_dict),
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count,
            "columns": list(data.columns),
            "data": _sanitize_for_json(data_dict)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV data: {str(e)}")

@app.get("/v1/ml/data/sample", tags=["Member B: ML Anomaly Detection"])
def get_csv_data_sample(limit: int = 100):
    """
    Member B: Get a sample of CSV data from the data folder
    Returns a limited number of records for testing purposes
    
    Parameters:
    - limit: Number of records to return (default: 100, max: 10000)
    """
    try:
        # Path to the CSV file in the data folder
        csv_path = os.path.join(project_root, "data", "base_txns_10k_ml_slim.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV data file not found")
        
        # Limit the sample size to prevent issues
        limit = min(limit, 10000)  # Cap at 10000 records for samples (full dataset)
        
        # Read the CSV data with limit
        data = pd.read_csv(csv_path, nrows=limit)
        
        # Convert to JSON-safe format
        data_dict = data.to_dict(orient="records")
        
        return {
            "status": "success",
            "file_path": csv_path,
            "limit": limit,
            "count": len(data_dict),
            "columns": list(data.columns),
            "data": _sanitize_for_json(data_dict)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV data: {str(e)}")

@app.get("/v1/ml/data/chunks", tags=["Member B: ML Anomaly Detection"])
def get_csv_data_chunks(chunk_size: int = 1000):
    """
    Member B: Get CSV data in manageable chunks
    Returns information about how to paginate through all data
    
    Parameters:
    - chunk_size: Size of each chunk (default: 1000, max: 10000)
    """
    try:
        # Path to the CSV file in the data folder
        csv_path = os.path.join(project_root, "data", "base_txns_10k_ml_slim.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV data file not found")
        
        # Limit chunk size
        chunk_size = min(chunk_size, 10000)  # Allow up to full dataset
        
        # Get total count efficiently
        total_count = len(pd.read_csv(csv_path, usecols=[0]))
        
        # Calculate number of chunks needed
        total_chunks = (total_count + chunk_size - 1) // chunk_size
        
        return {
            "status": "success",
            "file_path": csv_path,
            "total_count": total_count,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "instructions": {
                "message": "Use /v1/ml/data with limit and offset parameters to get chunks",
                "example_urls": [
                    f"/v1/ml/data?limit={chunk_size}&offset=0",
                    f"/v1/ml/data?limit={chunk_size}&offset={chunk_size}",
                    f"/v1/ml/data?limit={chunk_size}&offset={chunk_size * 2}"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get CSV data info: {str(e)}")

@app.get("/v1/ml/data/info", tags=["Member B: ML Anomaly Detection"])
def get_csv_data_info():
    """
    Member B: Get information about the CSV data file
    Returns metadata about the dataset without loading all data
    """
    try:
        # Path to the CSV file in the data folder
        csv_path = os.path.join(project_root, "data", "base_txns_10k_ml_slim.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV data file not found")
        
        # Get file info
        file_stats = os.stat(csv_path)
        
        # Read just the header to get column info
        data_sample = pd.read_csv(csv_path, nrows=0)
        
        return {
            "status": "success",
            "file_path": csv_path,
            "file_size_bytes": file_stats.st_size,
            "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
            "columns": list(data_sample.columns),
            "column_count": len(data_sample.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get CSV data info: {str(e)}")

@app.post("/v1/ml/detect", tags=["Member B: ML Anomaly Detection"])
def ml_detect(req: MLDetectionRequest):
    """
    Member B: Run full ML anomaly detection pipeline
    Requires a CSV file with transaction data
    """
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")

    try:
        # Load data
        data = pd.read_csv(req.file_path)
        
        # Initialize detector
        detector = AnomalyDetector(data, target_column="isFraud", svm_sample_size=10000)
        
        # Train models
        detector.fit()
        try:
            detector.train_xgboost()
        except Exception as e:
            print(f"XGBoost training skipped: {e}")
        
        # Generate predictions
        results = detector.predict()
        results = detector.add_risk_scores(results)
        results = detector.add_shap_explanations(results, model_name="IsolationForest")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results,
            "models_used": ["IsolationForest", "OneClassSVM", "XGBoost"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML detection failed: {str(e)}")

@app.post("/v1/ml/detect-from-transactions", tags=["Member B: ML Anomaly Detection"])
def ml_detect_from_transactions(req: ScoreRequest):
    """
    Member B: Run ML detection directly on transaction data (no file required)
    """
    try:
        # Convert transactions to DataFrame
        df = pd.DataFrame([t.model_dump() for t in req.transactions])
        
        # Initialize detector
        detector = AnomalyDetector(df, target_column="isFraud" if "isFraud" in df.columns else None, svm_sample_size=10000)
        
        # Train models
        detector.fit()
        if "isFraud" in df.columns:
            try:
                detector.train_xgboost()
            except Exception as e:
                print(f"XGBoost training skipped: {e}")
        
        # Generate predictions
        results = detector.predict()
        if "isFraud" in df.columns:
            results = detector.add_risk_scores(results)
        results = detector.add_shap_explanations(results, model_name="IsolationForest")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results,
            "models_used": ["IsolationForest", "OneClassSVM"] + (["XGBoost"] if "isFraud" in df.columns else [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML detection failed: {str(e)}")

@app.post("/v1/ml/detect-from-csv", tags=["Member B: ML Anomaly Detection"])
def ml_detect_from_csv():
    """
    Member B: Run ML detection directly on the CSV data from the data folder
    Convenient endpoint that uses the built-in CSV file
    """
    try:
        # Path to the CSV file in the data folder
        csv_path = os.path.join(project_root, "data", "base_txns_10k_ml_slim.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV data file not found")
        
        # Load data
        data = pd.read_csv(csv_path)
        
        # Initialize detector
        detector = AnomalyDetector(data, target_column="isFraud", svm_sample_size=10000)
        
        # Train models
        detector.fit()
        try:
            detector.train_xgboost()
        except Exception as e:
            print(f"XGBoost training skipped: {e}")
        
        # Generate predictions
        results = detector.predict()
        results = detector.add_risk_scores(results)
        results = detector.add_shap_explanations(results, model_name="IsolationForest")
        
        return {
            "status": "success",
            "file_path": csv_path,
            "count": len(results),
            "results": results,
            "models_used": ["IsolationForest", "OneClassSVM", "XGBoost"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML detection failed: {str(e)}")

# ------------ Unified Route (Both Members A & B) ------------

@app.post("/v1/unified/score", tags=["Unified: Members A & B"])
def unified_score(req: UnifiedRequest):
    """
    UNIFIED ENDPOINT: Combines both Member A and Member B's analysis
    Returns integrated results with both graph scores and ML anomaly scores
    """
    results = {
        "status": "success",
        "count": len(req.transactions),
        "graph_analysis": None,
        "ml_detection": None,
        "integrated_results": []
    }
    
    # Run Member A's graph analysis
    if req.run_graph_analysis:
        try:
            df = pd.DataFrame([t.model_dump() for t in req.transactions])
            needed = ["idx","step","type","amount","nameOrig","nameDest"]
            missing = [c for c in needed if c not in df.columns]
            
            if not missing:
                df_filtered = df[df["type"].isin(["TRANSFER","CASH_OUT"])].copy()
                graph_results = score_batch(df_filtered)
                results["graph_analysis"] = {
                    "count": len(graph_results),
                    "results": graph_results
                }
        except Exception as e:
            results["graph_analysis"] = {"error": str(e)}
    
    # Run Member B's ML detection
    if req.run_ml_detection:
        try:
            df = pd.DataFrame([t.model_dump() for t in req.transactions])
            detector = AnomalyDetector(df, target_column="isFraud" if "isFraud" in df.columns else None, svm_sample_size=10000)
            detector.fit()
            if "isFraud" in df.columns:
                try:
                    detector.train_xgboost()
                except Exception as e:
                    print(f"XGBoost training skipped: {e}")
            
            ml_results = detector.predict()
            if "isFraud" in df.columns:
                ml_results = detector.add_risk_scores(ml_results)
            
            results["ml_detection"] = {
                "count": len(ml_results),
                "results": ml_results
            }
        except Exception as e:
            results["ml_detection"] = {"error": str(e)}
    
    # Merge results if both ran successfully
    if (results["graph_analysis"] and "results" in results["graph_analysis"] and 
        results["ml_detection"] and "results" in results["ml_detection"]):
        
        graph_df = pd.DataFrame(results["graph_analysis"]["results"])
        ml_df = pd.DataFrame(results["ml_detection"]["results"])
        
        # Merge on transaction_id (ml) and idx (graph)
        ml_df = ml_df.rename(columns={"transaction_id": "idx"})
        merged = pd.merge(graph_df, ml_df, on="idx", how="outer")
        
        results["integrated_results"] = merged.to_dict(orient="records")
    
    return _sanitize_for_json(results)

# ------------ Legacy Member B Route (for backward compatibility) ------------

@app.post("/run-agentB", tags=["Legacy: Member B"])
def run_agent_b(data: MLDetectionRequest):
    """
    Legacy Member B endpoint (backward compatible)
    Redirects to new /v1/ml/detect endpoint
    """
    return ml_detect(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

def main():
    """Entry point for console script"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
