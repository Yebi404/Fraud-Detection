# api/app.py
from typing import List, Any, Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
import pandas as pd

from src.graph_scoring import score_batch, build_graph
from src.precision_scoring import precision_for_txn

app = FastAPI(
    title="Graph & Link Analysis Agent",
    version="1.0.0",
    description="Fraud-ring detector service. FAST batch scoring + on-demand precision refinement.",
)

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
    transactions: List[Txn]  # small batch to rebuild local graph context
    focus_idx: int

# ------------ Routes ------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/graph/score", response_model=ScoreResponse)
def graph_score(req: ScoreRequest):
    df = pd.DataFrame([t.model_dump() for t in req.transactions])

    needed = ["idx","step","type","amount","nameOrig","nameDest"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        return {"count": 0, "results": [], "warning": f"Missing columns: {missing}"}

    df = df[df["type"].isin(["TRANSFER","CASH_OUT"])].copy()
    results = score_batch(df)
    return {"count": len(results), "results": results}

@app.post("/v1/graph/precision")
def graph_precision(req: PrecisionRequest):
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
