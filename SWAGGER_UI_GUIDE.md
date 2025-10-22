# 📘 Swagger UI Guide - Integrated Fraud Detection API

## 🎯 Quick Access

**Swagger UI is now running at:**
```
http://127.0.0.1:8001/docs
```

**Alternative Documentation:**
- **ReDoc**: http://127.0.0.1:8001/redoc
- **OpenAPI Schema**: http://127.0.0.1:8001/openapi.json

---

## ✅ What You Can See in Swagger UI

The Swagger UI is organized into **3 sections**:

### 1️⃣ **Member A: Graph Analysis**
- `GET /health` - Check if API is running
- `POST /v1/graph/score` - Batch graph scoring
- `POST /v1/graph/precision` - Detailed 7d/30d analysis

### 2️⃣ **Member B: ML Anomaly Detection**
- `POST /v1/ml/detect` - ML detection from CSV file
- `POST /v1/ml/detect-from-transactions` - ML detection from JSON
- `POST /run-agentB` - Legacy endpoint

### 3️⃣ **Unified: Members A & B Combined**
- `POST /v1/unified/score` - **Combined graph + ML analysis**

---

## 🚀 How to Use Swagger UI

### Step 1: Open Swagger UI
1. Make sure the API is running:
   ```bash
   python -m uvicorn api.unified_app:app --reload --port 8001
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:8001/docs
   ```

### Step 2: Test an Endpoint

#### Example: Testing `/health` Endpoint

1. **Click** on `GET /health` to expand it
2. **Click** the "Try it out" button
3. **Click** "Execute"
4. **See** the response:
   ```json
   {
     "status": "ok",
     "service": "Integrated Fraud Detection (Members A & B)",
     "version": "2.0.0"
   }
   ```

---

## 🧪 Testing Member A Endpoints

### Test 1: Batch Graph Scoring

**Endpoint**: `POST /v1/graph/score`

1. Click on the endpoint to expand
2. Click "Try it out"
3. Copy this JSON into the request body:

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
    },
    {
      "idx": 2,
      "step": 96,
      "type": "TRANSFER",
      "amount": 2000,
      "nameOrig": "U2",
      "nameDest": "R1"
    },
    {
      "idx": 3,
      "step": 97,
      "type": "CASH_OUT",
      "amount": 1500,
      "nameOrig": "U3",
      "nameDest": "R1"
    }
  ]
}
```

4. Click "Execute"
5. **Expected Response**:
```json
{
  "count": 3,
  "results": [
    {
      "idx": 1,
      "step": 95,
      "txn_user": "U1",
      "txn_receiver": "R1",
      "amount": 1000.0,
      "type": "TRANSFER",
      "ring_score_7d": 0.7391,
      "confidence": null,
      "precision_enhanced": false
    },
    // ... more results
  ]
}
```

---

### Test 2: Precision Analysis (7d vs 30d)

**Endpoint**: `POST /v1/graph/precision`

1. Click to expand
2. Click "Try it out"
3. Use this JSON:

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

4. Click "Execute"
5. **Expected Response**:
```json
{
  "focus_idx": 1,
  "ring_score_7d": 0.8234,
  "ring_score_30d": 0.7865,
  "delta_score": 0.0369,
  "reasons_7d": [
    {
      "feature": "shared_receiver_degree",
      "value": 12,
      "impact": 0.21
    }
  ],
  "reasons_30d": [...]
}
```

---

## 🤖 Testing Member B Endpoints

### Test 3: ML Detection from Transactions

**Endpoint**: `POST /v1/ml/detect-from-transactions`

1. Click to expand
2. Click "Try it out"
3. Use this JSON:

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
    },
    {
      "idx": 2,
      "step": 96,
      "type": "TRANSFER",
      "amount": 50000,
      "nameOrig": "U2",
      "nameDest": "R1",
      "isFraud": 1
    }
  ]
}
```

4. Click "Execute"
5. **Expected Response**:
```json
{
  "status": "success",
  "count": 2,
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

---

## 🎯 Testing Unified Endpoint (BEST FOR DEMO!)

### Test 4: Combined Graph + ML Analysis

**Endpoint**: `POST /v1/unified/score`

This is the **MAIN ENDPOINT** that combines both Member A and Member B!

1. Click to expand
2. Click "Try it out"
3. Use this complete JSON:

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
    },
    {
      "idx": 2,
      "step": 96,
      "type": "TRANSFER",
      "amount": 2000,
      "nameOrig": "U2",
      "nameDest": "R1",
      "isFraud": 0
    },
    {
      "idx": 3,
      "step": 97,
      "type": "TRANSFER",
      "amount": 50000,
      "nameOrig": "U3",
      "nameDest": "R2",
      "isFraud": 1
    }
  ],
  "run_ml_detection": true,
  "run_graph_analysis": true
}
```

4. Click "Execute"
5. **Expected Response** (Combined Results!):
```json
{
  "status": "success",
  "count": 3,
  "graph_analysis": {
    "count": 3,
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
    "count": 3,
    "results": [
      {
        "transaction_id": 0,
        "anomaly_score": 0.45
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

**This shows both Member A and Member B working together!** ✨

---

## 📁 Using Test Data Files

You can also test with pre-made test files:

### Option 1: Load from File
1. In Swagger UI, click "Try it out"
2. You'll see a text area for the JSON
3. Open one of these files in a text editor:
   - `tests/sample_request.json`
   - `tests/better_test_data.json`
   - `tests/fraud_ring_scenario.json`
4. Copy the entire content
5. Paste into Swagger UI
6. Click "Execute"

### Option 2: Use cURL (from terminal)
```bash
curl -X POST "http://127.0.0.1:8001/v1/unified/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

---

## 🎨 Swagger UI Features

### Color Coding
- 🟢 **Green (GET)** - Read operations
- 🟠 **Orange (POST)** - Create/Execute operations
- 🔵 **Blue** - Information

### Sections in Each Endpoint
1. **Parameters** - What you need to send
2. **Request body** - JSON structure with example
3. **Responses** - What you'll get back
4. **Try it out** - Interactive testing
5. **Response** - Shows actual results

### Understanding Responses

#### Response Code Meanings:
- **200 OK** ✅ - Success
- **422 Unprocessable Entity** ⚠️ - Invalid input format
- **500 Internal Server Error** ❌ - Server error

---

## 🔍 Common Issues & Solutions

### Issue 1: 422 Error - Validation Error
**Problem**: Missing required fields or wrong data types

**Solution**: Make sure your JSON includes:
- `idx` (integer)
- `step` (integer)
- `type` (string: "TRANSFER", "CASH_OUT", etc.)
- `amount` (number)
- `nameOrig` (string)
- `nameDest` (string)
- `isFraud` (optional, integer: 0 or 1)

### Issue 2: API Not Responding
**Problem**: Server not running

**Solution**: 
```bash
python -m uvicorn api.unified_app:app --reload --port 8001
```

### Issue 3: Port Already in Use
**Problem**: Port 8001 is occupied

**Solution**: Use a different port:
```bash
python -m uvicorn api.unified_app:app --reload --port 8002
```
Then access: http://127.0.0.1:8002/docs

---

## 🎬 Demo Walkthrough

### Perfect Demo Flow:

1. **Start API**:
   ```bash
   python -m uvicorn api.unified_app:app --reload --port 8001
   ```

2. **Open Swagger UI**: http://127.0.0.1:8001/docs

3. **Show Health Check**:
   - Test `GET /health`
   - Show it returns "ok"

4. **Show Member A (Graph Analysis)**:
   - Test `POST /v1/graph/score`
   - Show ring scores being calculated

5. **Show Member B (ML Detection)**:
   - Test `POST /v1/ml/detect-from-transactions`
   - Show ML anomaly scores

6. **FINALE - Show Unified Endpoint**:
   - Test `POST /v1/unified/score`
   - Show **BOTH graph scores AND ML scores together!**
   - Point out the `integrated_results` section

7. **Explain Handoff**:
   - Show how `idx` field merges everything
   - Explain Members C & D can use these results

---

## 📊 Response Field Explanations

### Member A Fields (Graph Analysis):
| Field | Meaning |
|-------|---------|
| `ring_score_7d` | Fraud risk based on 7-day graph analysis (0-1) |
| `ring_score_30d` | Fraud risk based on 30-day graph analysis (0-1) |
| `component_size` | Size of connected network component |
| `pagerank_user` | User's PageRank score in the network |
| `delta_score` | Difference between 7d and 30d scores |

### Member B Fields (ML Detection):
| Field | Meaning |
|-------|---------|
| `anomaly_score` | Combined anomaly score from IF+SVM (0-1) |
| `ml_score` | Ensemble ML score (0-1) |
| `ml_supervised` | XGBoost probability (0-1, if labels provided) |
| `risk_score_baseline` | Supervised risk score |
| `top_features` | Most important features (SHAP) |
| `explanation` | SHAP values for interpretability |

### Integrated Fields:
All of the above **merged on the `idx` field**!

---

## 💡 Pro Tips

1. **Save Your Requests**: Swagger UI remembers your last request in the session
2. **Use Schema Button**: Click "Schema" to see the exact JSON structure
3. **Download OpenAPI**: Save the spec from `/openapi.json` for external tools
4. **Copy cURL**: After executing, Swagger shows the equivalent cURL command
5. **Expand All**: Use "Expand Operations" to see all endpoints at once

---

## 🆘 Need Help?

### Quick Reference:
- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc (alternative UI)
- **Health Check**: http://127.0.0.1:8001/health
- **Test Data**: `tests/` folder

### Documentation:
- `START_HERE.md` - Quick start
- `QUICKSTART.md` - Detailed setup
- `README.md` - Complete guide
- `docs/api.md` - API reference

---

## ✅ You're Ready!

**Swagger UI is fully functional and ready for your demo!**

Just:
1. Start the API: `python -m uvicorn api.unified_app:app --reload --port 8001`
2. Open: http://127.0.0.1:8001/docs
3. Test the `/v1/unified/score` endpoint
4. Show both Member A and Member B working together!

**Good luck! 🚀**






