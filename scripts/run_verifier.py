# scripts/run_verifier.py
import sys
import os
import requests
import json

# Fix Python path so 'agents' module can be found
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.transaction_verifier import TransactionVerifierAgent

def main():
    # 1️⃣ Member B's API URL
    member_b_api_url = "http://10.90.132.1:8001/run-agentB"

    # 2️⃣ Path to Member A's output (local CSV)
    ring_path = os.path.join("data", "ring_scores_window.csv")
    if not os.path.exists(ring_path):
        print(f"❌ Missing Member A's output CSV: {ring_path}")
        return

    # 3️⃣ Call Member B's API
    print("🔗 Calling Member B's API...")

    payload = {
        "file_path": "data/base_txns_full_for_ml.csv"  # path on Member B's machine
    }

    try:
        response = requests.post(member_b_api_url, json=payload, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Member B's API: {e}")
        return

    print("DEBUG: API response status code:", response.status_code)
    print("DEBUG: API response content:", response.text)

    if response.status_code != 200:
        print("❌ Member B API returned HTTP error:", response.text)
        return

    try:
        result = response.json()
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from Member B API")
        return

    if result.get("status") != "success":
        print("❌ Member B API returned error:", result)
        return

    # 4️⃣ Save Member B's ml_scores.csv locally
    ml_csv_content = result.get("ml_scores_csv_content", "")
    ml_path = os.path.join("data", "ml_scores.csv")
    with open(ml_path, "w") as f:
        f.write(ml_csv_content)

    # 5️⃣ Save anomaly JSON locally
    anomaly_json_content = result.get("anomaly_json_content", {})
    anomaly_json_path = os.path.join("models", "anomaly_output_standard.json")
    with open(anomaly_json_path, "w") as f:
        json.dump(anomaly_json_content, f, indent=4)

    # 6️⃣ Output path for Member C's verification report
    out_path = os.path.join("models", "verification_report.json")

    # 7️⃣ Run the verification agent
    agent = TransactionVerifierAgent(
        ring_csv=ring_path,
        ml_csv=ml_path,
        output_json=out_path
    )
    path = agent.run()
    print(f"✅ Report saved at {path}")

if __name__ == "__main__":
    main()
