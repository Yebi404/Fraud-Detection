import os
import sys
import pandas as pd

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.anomaly_detector import AnomalyDetector

# Paths
DATA_PATH = "data/base_txns_full_for_ml.csv"
JSON_OUT = "models/anomaly_output_standard.json"
CSV_OUT  = "models/ml_scores.csv"

def main():
    # 1) Load data
    assert os.path.exists(DATA_PATH), f"Missing data file: {DATA_PATH}"
    data = pd.read_csv(DATA_PATH)
    print(f"Loaded {DATA_PATH} with shape {data.shape}")

    # 2) Initialize detector
    detector = AnomalyDetector(data, target_column="isFraud", svm_sample_size=10000)

    # 3) Train unsupervised models
    detector.fit()

    # 4) Train supervised model
    detector.train_xgboost()

    # 5) Evaluate on test set
    detector.evaluate_model()

    # 6) Save JSON output
    detector.save_standardized_results(filename=JSON_OUT, model_name="IsolationForest")

    # 7) Save CSV output
    detector.export_ml_scores_csv(out_path=CSV_OUT, include_supervised=True, shap_top_n=5)

    print("\nDone.")
    print(f"- JSON : {JSON_OUT}")
    print(f"- CSV  : {CSV_OUT}")

if __name__ == "__main__":
    main()
