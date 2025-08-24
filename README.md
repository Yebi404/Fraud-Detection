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
