Create docs/api.md:

# API

## GET /health
200 OK → `{"status":"ok"}`

## POST /v1/graph/score
Batch FAST scoring.

**Request**
```json
{
  "transactions": [
    {"idx":1,"step":95,"type":"TRANSFER","amount":1000,"nameOrig":"U1","nameDest":"R1"}
  ]
}


Response

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

POST /v1/graph/precision

Refine one focus transaction using 7d/30d subgraphs.

Request

{
  "transactions":[{"idx":1,"step":95,"type":"TRANSFER","amount":1000,"nameOrig":"U1","nameDest":"R1"}],
  "focus_idx": 1
}


Response

{
  "focus_idx": 1,
  "ring_score_7d": 0.88,
  "ring_score_30d": 0.70,
  "delta_score": 0.18,
  "reasons_7d": [{"feature":"shared_receiver_degree","value":12,"impact":0.21}],
  "reasons_30d": [{"feature":"shared_receiver_degree","value":35,"impact":0.18}]
}


Create `docs/architecture.md`:

```md
# Pipeline Architecture

Raw Transactions → **Member A: Graph Agent** → Graph-based scores JSON  
                   ↘ **Member B: ML Anomaly Detector** → ml_score + SHAP  
                    ↘ **Member C: Verifier Agent** → verifier_verdict + reason  
                     ↘ **Member D: UI/Alerts** → merged table + ring HTML link

Shared key for merging: `idx`

Week-6: file hand-off (CSVs/JSON).  
Final: services call `/v1/graph/score` and (optional) `/v1/graph/precision`.