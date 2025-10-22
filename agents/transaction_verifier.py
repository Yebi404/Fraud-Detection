# agents/transaction_verifier.py
import os, json, math
import pandas as pd
import numpy as np

class VerifierConfig:
    ml_score_flag = 0.40
    ml_score_deny = 0.75
    ring_score_flag = 0.80
    ring_score_deny = 0.95
    velocity_window_steps = 6
    velocity_flag = 3
    velocity_deny = 10
    amount_hi_quantile = 0.99
    weight_ml = 0.6
    weight_ring = 0.4

class TransactionVerifierAgent:
    def __init__(self, ring_csv, ml_csv, output_json, blacklist_csv=None, cfg=None):
        self.ring_csv = ring_csv
        self.ml_csv = ml_csv
        self.output_json = output_json
        self.blacklist_csv = blacklist_csv
        self.cfg = cfg or VerifierConfig()

    def run(self):
        # Read input files
        ring_df = pd.read_csv(self.ring_csv)
        ml_df = pd.read_csv(self.ml_csv)

        # Ensure ml_score exists
        if "ml_score" not in ml_df.columns:
            numeric_cols = ml_df.drop(columns=["idx"]).select_dtypes(include=[np.number])
            ml_df["ml_score"] = numeric_cols.mean(axis=1)

        # Create a combined ring_score from both 7-day and 30-day
        if "ring_score_7d" in ring_df.columns and "ring_score_30d" in ring_df.columns:
            ring_df["ring_score"] = (ring_df["ring_score_7d"] + ring_df["ring_score_30d"]) / 2
        elif "ring_score_7d" in ring_df.columns:
            ring_df["ring_score"] = ring_df["ring_score_7d"]
        elif "ring_score_30d" in ring_df.columns:
            ring_df["ring_score"] = ring_df["ring_score_30d"]
        else:
            ring_df["ring_score"] = 0.0  # fallback default if both missing

        # Merge on 'idx'
        df = pd.merge(ring_df, ml_df, on="idx", how="inner")

        # Calculate combined score using weights
        df["combined_score"] = (self.cfg.weight_ml * df["ml_score"] +
                                self.cfg.weight_ring * df["ring_score"])

        # Determine status based on thresholds
        df["status"] = "pass"
        df.loc[df["combined_score"] >= self.cfg.ml_score_deny, "status"] = "deny"
        df.loc[df["combined_score"].between(self.cfg.ml_score_flag, self.cfg.ml_score_deny), "status"] = "flag"

        # Create explanations
        df["explanation"] = df.apply(
            lambda r: (f"Transaction {r['idx']} has ml_score={r['ml_score']:.2f}, "
                       f"ring_score={r['ring_score']:.2f}, "
                       f"combined_score={r['combined_score']:.2f}, status={r['status']}"), axis=1
        )

        # Build report
        report = {
            "meta": {
                "total": len(df),
                "deny": int(sum(df["status"] == "deny")),
                "flag": int(sum(df["status"] == "flag")),
                "pass": int(sum(df["status"] == "pass")),
            },
            "data": df[["idx", "status", "ml_score", "ring_score", "combined_score", "explanation"]].to_dict(orient="records")
        }

        # Save JSON output
        os.makedirs(os.path.dirname(self.output_json), exist_ok=True)
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return self.output_json
