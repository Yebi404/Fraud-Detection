# Graph & Link Analysis Agent (Member A)

Production-style service for graph-based fraud-ring detection.

- `POST /v1/graph/score` → FAST batch scoring (global graph features)
- `POST /v1/graph/precision` → refine one transaction using 7d/30d subgraphs
- OpenAPI docs at `http://localhost:8001/docs`

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.app:app --reload --port 8001
```

### Test

```bash
curl -X POST "http://localhost:8001/v1/graph/score" \
  -H "Content-Type: application/json" \
  -d @tests/sample_request.json
```

## Repo Layout

```
api/app.py                # API entry
src/graph_scoring.py      # FAST pass
src/precision_scoring.py  # 7d/30d refine (single focus txn)
tests/                    # sample request + tests
outputs/                  # artifacts from notebook (CSV, HTML graphs)
docs/                     # api + architecture + responsible AI
notebooks/                # your Colab analysis (EDA, metrics, visuals)
```

## Notes

* This service mirrors the validated notebook logic with a lighter online path (FAST) and an on-demand precision path.
* For the final demo, UI (Member D) can call these endpoints or load `outputs/` artifacts as backup.

## Hand-off message to your team

> **Member A – Graph Agent (Final)**
>
> * Repo: `<your GitHub URL>`
> * Endpoints:
>
>   * `POST /v1/graph/score` (FAST batch)
>   * `POST /v1/graph/precision` (refine one `idx` with 7d/30d)
> * Docs: `http://localhost:8001/docs` and `docs/api.md`
> * Sample request: `tests/sample_request.json`
> * Backup artifacts for UI: `outputs/` (CSV + HTML ring graphs)
> * Shared key: `idx`
>   **Please integrate:**
> * **B**: join `ml_score` on `idx` with my results
> * **C**: add `verifier_verdict` and `verifier_reason`
> * **D**: display merged table; click opens `fraud_ring_7d.html` or call `/v1/graph/precision`
