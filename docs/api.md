# Integrated Fraud Detection API Reference

This API combines **Member A's Graph Analysis** and **Member B's ML Anomaly Detection** capabilities.

## Base URL
```
http://localhost:8001
```

## Common Data Models

### Transaction Object
```json
{
  "idx": 1,                    // Unique transaction ID (required)
  "step": 95,                  // Time step (required)
  "type": "TRANSFER",          // Transaction type (required)
  "amount": 1000.0,            // Amount (required)
  "nameOrig": "U1",            // Sender (required)
  "nameDest": "R1",            // Receiver (required)
  "isFraud": 0                 // Fraud label (optional)
}
```

---

## Health Check

### `GET /health`

Check service health status.

**Response**
```json
{
  "status": "ok",
  "service": "Integrated Fraud Detection (Members A & B)",
  "version": "2.0.0"
}
```

---

## Member A: Graph Analysis Endpoints

### `POST /v1/graph/score`

**FAST batch graph scoring** using network analysis.

**Request**
```json
{
  "transactions": [
    {
      "idx": 1,
      "step": 95,
      "type": "TRANSFER",
      "amount": 1000,
      "nameOrig": "U1",
      "nameDest": "R1"
    }
  ]
}
```

**Response**
```json
{
  "count": 1,
  "results": [
    {
      "idx": 1,
      "step": 95,
      "txn_user": "U1",
      "txn_receiver": "R1",
      "amount": 1000.0,
      "type": "TRANSFER",
      "ring_score_7d": 0.82,
      "confidence": null,
      "precision_enhanced": false
    }
  ]
}
```

**Features Used:**
- Component size
- Shared receiver degree
- PageRank score

---

### `POST /v1/graph/precision`

**Detailed precision analysis** for a single transaction using 7-day vs 30-day subgraph comparison.

**Request**
```json
{
  "transactions": [
    {
      "idx": 1,
      "step": 95,
      "type": "TRANSFER",
      "amount": 1000,
      "nameOrig": "U1",
      "nameDest": "R1"
    }
  ],
  "focus_idx": 1
}
```

**Response**
```json
{
  "focus_idx": 1,
  "ring_score_7d": 0.88,
  "ring_score_30d": 0.70,
  "delta_score": 0.18,
  "reasons_7d": [
    {
      "feature": "shared_receiver_degree",
      "value": 12,
      "impact": 0.21
    }
  ],
  "reasons_30d": [
    {
      "feature": "shared_receiver_degree",
      "value": 35,
      "impact": 0.18
    }
  ]
}
```

**Additional Features:**
- K-core number
- Community size (Louvain)
- Temporal burst patterns
- U-R-U motif counts

---

## Member B: ML Anomaly Detection Endpoints

### `POST /v1/ml/detect`

**Run ML anomaly detection** from a CSV file.

**Request**
```json
{
  "file_path": "data/transactions.csv"
}
```

**Response**
```json
{
  "status": "success",
  "count": 100,
  "results": [
    {
      "transaction_id": 0,
      "anomaly_score": 0.65,
      "risk_score_baseline": 0.72,
      "top_features": ["amount", "step", "type_TRANSFER"],
      "explanation": {
        "amount": 0.15,
        "step": 0.08,
        "type_TRANSFER": 0.05
      }
    }
  ],
  "models_used": ["IsolationForest", "OneClassSVM", "XGBoost"]
}
```

---

### `POST /v1/ml/detect-from-transactions`

**Run ML detection** directly on transaction data (no file required).

**Request**
```json
{
  "transactions": [
    {
      "idx": 1,
      "step": 95,
      "type": "TRANSFER",
      "amount": 1000,
      "nameOrig": "U1",
      "nameDest": "R1",
      "isFraud": 0
    }
  ]
}
```

**Response**
```json
{
  "status": "success",
  "count": 1,
  "results": [
    {
      "transaction_id": 0,
      "anomaly_score": 0.45,
      "risk_score_baseline": 0.38,
      "top_features": ["amount", "step"],
      "explanation": {
        "amount": 0.12,
        "step": 0.06
      }
    }
  ],
  "models_used": ["IsolationForest", "OneClassSVM", "XGBoost"]
}
```

**Models Used:**
- **Isolation Forest**: Unsupervised anomaly detection
- **One-Class SVM**: Novelty detection
- **XGBoost**: Supervised classification (if `isFraud` labels provided)
- **SHAP**: Feature importance and explanations

---

### `POST /run-agentB` (Legacy)

**Legacy endpoint** for backward compatibility. Redirects to `/v1/ml/detect`.

---

## Unified Endpoint (Members A & B Combined)

### `POST /v1/unified/score`

**Complete integrated analysis** combining both graph and ML detection.

**Request**
```json
{
  "transactions": [
    {
      "idx": 1,
      "step": 95,
      "type": "TRANSFER",
      "amount": 1000,
      "nameOrig": "U1",
      "nameDest": "R1",
      "isFraud": 0
    }
  ],
  "run_ml_detection": true,
  "run_graph_analysis": true
}
```

**Response**
```json
{
  "status": "success",
  "count": 1,
  "graph_analysis": {
    "count": 1,
    "results": [
      {
        "idx": 1,
        "ring_score_7d": 0.82,
        "txn_user": "U1",
        "txn_receiver": "R1"
      }
    ]
  },
  "ml_detection": {
    "count": 1,
    "results": [
      {
        "transaction_id": 0,
        "anomaly_score": 0.45,
        "risk_score_baseline": 0.38
      }
    ]
  },
  "integrated_results": [
    {
      "idx": 1,
      "ring_score_7d": 0.82,
      "anomaly_score": 0.45,
      "ml_score": 0.38,
      "amount": 1000.0,
      "type": "TRANSFER"
    }
  ]
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "File not found: data/missing.csv"
}
```

### 500 Internal Server Error
```json
{
  "detail": "ML detection failed: insufficient data"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "transactions", 0, "idx"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Integration Examples

### Python Example
```python
import requests
import pandas as pd

# Load transactions
df = pd.read_csv("data/transactions.csv")
transactions = df.to_dict(orient='records')

# Call unified endpoint
response = requests.post(
    "http://localhost:8001/v1/unified/score",
    json={
        "transactions": transactions,
        "run_ml_detection": True,
        "run_graph_analysis": True
    }
)

results = response.json()
integrated_df = pd.DataFrame(results["integrated_results"])
print(integrated_df[["idx", "ring_score_7d", "anomaly_score"]].head())
```

### cURL Example
```bash
# Member A: Graph scoring
curl -X POST "http://localhost:8001/v1/graph/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json

# Member B: ML detection
curl -X POST "http://localhost:8001/v1/ml/detect" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/transactions.csv"}'

# Unified: Both A & B
curl -X POST "http://localhost:8001/v1/unified/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

---

## Interactive Documentation

Visit the auto-generated Swagger UI documentation:
```
http://localhost:8001/docs
```

Or ReDoc format:
```
http://localhost:8001/redoc
```
