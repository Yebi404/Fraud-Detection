from fastapi import FastAPI
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