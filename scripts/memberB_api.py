from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="IRWA Fraud API")

# Load your anomaly score file
df = pd.read_csv("model/anomaly_scores_for_verifier.csv")

@app.get("/")
def home():
    return {"message": "IRWA Fraud API is running!", "total_records": len(df)}

@app.get("/scores")
def get_scores():
    """Return ML scores for all transactions"""
    return df[["idx", "ml_score"]].to_dict(orient="records")

@app.get("/health")
def health_check():
    """Simple health check"""
    return {"status": "ok", "records": len(df)}

# ADD THIS NEW ENDPOINT:
class TransactionRequest(BaseModel):
    transaction_id: str = None
    idx: int = None

@app.post("/run-agentB")
def run_agent_b(request: TransactionRequest = None):
    """
    Main endpoint for Member A's verifier to call
    Returns anomaly scores for verification
    """
    try:
        if request and request.idx is not None:
            # Return specific transaction score
            result = df[df["idx"] == request.idx]
            if result.empty:
                raise HTTPException(status_code=404, detail="Transaction not found")
            return result.to_dict(orient="records")[0]
        else:
            # Return all scores
            return {
                "status": "success",
                "message": "Anomaly scores ready",
                "total_records": len(df),
                "scores": df[["idx", "ml_score"]].to_dict(orient="records")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))