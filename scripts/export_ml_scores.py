# FRAUDDETECTIONAI/scripts/export_ml_scores.py
import os
import json
import pandas as pd

# Get script directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Absolute path to JSON
json_path = os.path.join(script_dir, "../models/anomaly_output_standard.json")

# Load JSON
with open(json_path, "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# ✅ Ensure required columns exist
if "transaction_id" not in df.columns:
    raise ValueError("JSON does not contain 'transaction_id' column")

# Build export DataFrame
df_handoff = pd.DataFrame()
df_handoff["idx"] = df["transaction_id"]

# Use supervised risk_score if available, otherwise anomaly_score
if "risk_score_baseline" in df.columns:
    df_handoff["ml_score"] = df["risk_score_baseline"]
    df_handoff["ml_supervised"] = df["risk_score_baseline"]  # API-consistent name
elif "anomaly_score" in df.columns:
    df_handoff["ml_score"] = df["anomaly_score"]
    df_handoff["ml_supervised"] = None  # no supervised score available
else:
    raise ValueError("JSON does not contain 'anomaly_score' or 'risk_score_baseline' columns")

# SHAP features if available
if "top_features" in df.columns:
    df_handoff["shap_top_features"] = df["top_features"].apply(lambda x: str(x) if x else "")
else:
    df_handoff["shap_top_features"] = ""

# Save CSV
csv_path = os.path.join(script_dir, "../models/ml_scores.csv")
df_handoff.to_csv(csv_path, index=False)

print(f"ML scores exported to {csv_path}")
