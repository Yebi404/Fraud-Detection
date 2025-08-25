# Pipeline Architecture

Raw Transactions → **Member A: Graph Agent (this service)** → Graph-based scores JSON  
                   ↘ **Member B: ML Anomaly Detector** → ml_score + SHAP  
                    ↘ **Member C: Verifier Agent** → verifier_verdict + reason  
                     ↘ **Member D: UI/Alerts** → merged table + ring HTML link

Shared key for merging: `idx`

Week-6: file hand-off (CSVs/JSON).  
Final: services call `/v1/graph/score` and (optional) `/v1/graph/precision`.
