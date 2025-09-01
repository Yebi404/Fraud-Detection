# scripts/run_verifier.py
import os
from agents.transaction_verifier import TransactionVerifierAgent

def main():
    ring_path = os.path.join("data", "ring_scores_window.csv")
    ml_path = os.path.join("data", "ml_scores.csv")
    out_path = os.path.join("models", "verification_report.json")

    agent = TransactionVerifierAgent(
        ring_csv=ring_path,
        ml_csv=ml_path,
        output_json=out_path
    )
    path = agent.run()
    print(f"✅ Report saved at {path}")
    
if __name__ == "__main__":
    main()
