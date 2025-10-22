from fastapi.testclient import TestClient
from api.unified_app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_score_minimal():
    payload = {"transactions":[
        {"idx":1,"step":95,"type":"TRANSFER","amount":1000,"nameOrig":"U1","nameDest":"R1"}
    ]}
    r = client.post("/v1/graph/score", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert js["count"] == 1
    assert "ring_score_7d" in js["results"][0]
