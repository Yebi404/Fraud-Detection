import sys
import os
import requests
import json
from typing import Optional, Iterable, Dict, Any

# Fix Python path so 'agents' module can be found
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.transaction_verifier import TransactionVerifierAgent

def ensure_directories_exist() -> None:
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)

def _rows_to_csv(rows: Iterable[Dict[str, Any]]) -> Optional[str]:
    rows = list(rows)
    if not rows:
        return None
    # prefer specific order when possible
    preferred = ["idx", "ml_score"]
    keys = list(rows[0].keys())
    # move preferred to front if present
    ordered = [k for k in preferred if k in keys] + [k for k in keys if k not in preferred]
    header = ",".join(ordered)
    lines = [header]
    for row in rows:
        values = [str(row.get(k, "")) for k in ordered]
        lines.append(",".join(values))
    return "\n".join(lines) + "\n"

def extract_ml_csv_content(result: Any) -> Optional[str]:
    # If the entire result is a list of rows
    if isinstance(result, list) and result:
        return _rows_to_csv(result)

    if not isinstance(result, dict):
        return None

    # Preferred: raw CSV content
    csv_content = result.get("ml_scores_csv_content")
    if isinstance(csv_content, str) and csv_content.strip():
        return csv_content

    # Alternate: downloadable URL to CSV
    ml_url = result.get("ml_scores_url")
    if isinstance(ml_url, str) and ml_url.startswith("http"):
        try:
            r = requests.get(ml_url, timeout=120)
            if r.status_code == 200 and r.text.strip():
                return r.text
        except requests.RequestException:
            pass

    # Alternate: structured data (list of dicts) → convert to CSV
    # Alternate: stringified JSON rows
    as_json = result.get("ml_scores_json") or result.get("ml_scores_str") or result.get("ml_scores")
    if isinstance(as_json, str) and as_json.strip():
        txt = as_json.strip()
        if txt.startswith("[") and txt.endswith("]"):
            try:
                parsed = json.loads(txt)
                if isinstance(parsed, list) and parsed:
                    return _rows_to_csv(parsed)
            except json.JSONDecodeError:
                pass

    # Alternate: rows in different keys or nested under data
    candidates = [
        result.get("ml_scores"), result.get("scores"), result.get("rows"), result.get("result"),
        (result.get("data") or {}).get("ml_scores") if isinstance(result.get("data"), dict) else None,
        (result.get("data") or {}).get("rows") if isinstance(result.get("data"), dict) else None,
    ]
    for rows in candidates:
        if isinstance(rows, list) and rows:
            return _rows_to_csv(rows)

    return None

def write_text_file(path: str, content: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def validate_ml_scores_csv(path: str) -> bool:
    # Lightweight validation without pandas
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f"❌ ML scores CSV missing or empty: {path}")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        if not first_line:
            print("❌ ML scores CSV has no header")
            return False
        headers = [h.strip() for h in first_line.split(",")]
        if "idx" not in headers or "ml_score" not in headers:
            print(f"❌ ML scores CSV must include 'idx' and 'ml_score' columns. Found: {headers}")
            return False
        return True
    except OSError:
        print("❌ Failed to read ML scores CSV for validation")
        return False

def main():
    print("🚀 Starting Transaction Verifier...")
    
    # 1️⃣ Member B's API URL
    member_b_api_url = "http://10.249.165.1:8001/run-agentB"
    print(f"📡 Member B API URL: {member_b_api_url}")

    # 2️⃣ Path to Member A's output (local CSV)
    ring_path = os.path.join("data", "ring_scores_window.csv")
    print(f"📁 Checking for ring scores at: {ring_path}")
    if not os.path.exists(ring_path):
        print(f"❌ Missing Member A's output CSV: {ring_path}")
        return
    print(f"✅ Ring scores found: {ring_path}")

    # 3️⃣ Call Member B's API
    print("Calling Member B's API...")

    payload = {
        "file_path": "data/base_txns_full_for_ml.csv"  # path on Member B's machine
    }

    try:
        response = requests.post(member_b_api_url, json=payload, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Member B's API: {e}")
        return

    print("DEBUG: API response status code:", response.status_code)
    print("DEBUG: API response content:", response.text)

    if response.status_code != 200:
        print("Member B API returned HTTP error:", response.text)
        return

    try:
        result = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON from Member B API")
        return

    if result.get("status") != "success":
        print("Member B API returned error:", result)
        return

    # 4️⃣ Save Member B's ml_scores.csv locally (robust handling)
    ensure_directories_exist()
    ml_csv_content = extract_ml_csv_content(result)
    ml_path = os.path.join("data", "ml_scores.csv")
    if not ml_csv_content:
        print("❌ Did not receive valid ML scores content from Member B (expected CSV content/url or rows)")
        if isinstance(result, dict):
            print("Debug: Top-level keys from Member B:", list(result.keys()))
            if "data" in result and isinstance(result["data"], dict):
                print("Debug: Data keys:", list(result["data"].keys()))
        else:
            print("Debug: Unexpected response type:", type(result))
        return
    write_text_file(ml_path, ml_csv_content)
    print(f"Saved ML scores CSV to {ml_path}")
    if not validate_ml_scores_csv(ml_path):
        print("Validation failed for ML scores CSV. Aborting before verification stage.")
        return

    # 5️⃣ Save anomaly JSON locally
    anomaly_json_content = result.get("anomaly_json_content", {})
    anomaly_json_path = os.path.join("models", "anomaly_output_standard.json")
    try:
        write_text_file(anomaly_json_path, json.dumps(anomaly_json_content, indent=4))
        print(f"Saved anomaly JSON to {anomaly_json_path}")
    except Exception as e:
        print(f"Failed to write anomaly JSON: {e}")

    # 6️⃣ Output path for Member C's verification report
    out_path = os.path.join("models", "verification_report.json")

    # 7️⃣ Run the verification agent
    agent = TransactionVerifierAgent(
        ring_csv=ring_path,
        ml_csv=ml_path,
        output_json=out_path
    )
    try:
        path = agent.run()
        print(f"✅ Report saved at {path}")
    except Exception as e:
        print(f"❌ Verifier failed to generate report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
     main()