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
