# FRAUDDETECTIONAI/agents/anomaly_detector.py
import os
import json
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

# SHAP is optional; only needed if you use XGBoost explainability
try:
    import shap  # noqa: F401
    _HAS_SHAP = True
except Exception:
    _HAS_SHAP = False


class AnomalyDetector:
    """
    Trains IsolationForest + One-Class SVM (unsupervised).
    Trains XGBoost on 'isFraud' (supervised).
    Exports:
      - JSON with per-row explanations (for audit)
      - CSV with model_if, model_svm, ml_score, supervised + SHAP features
    """

    def __init__(self, data: pd.DataFrame, svm_sample_size: int = 10000):
        self.data = data.copy()

        # ✅ Fixed label column for new dataset
        self.label_col = "isFraud"

        self.features = self.data.drop(columns=[self.label_col], errors="ignore")
        self.feature_names = self.features.columns.tolist()

        self.scaler = StandardScaler()
        self.data_scaled = self.scaler.fit_transform(self.features.values)

        self.svm_sample_size = svm_sample_size
        self.svm_data_scaled = resample(
            self.data_scaled,
            n_samples=min(svm_sample_size, len(self.data_scaled)),
            random_state=42,
            replace=False,
        )

        self.models = {
            "IsolationForest": IsolationForest(
                contamination=0.01, n_jobs=-1, random_state=42
            ),
            "OneClassSVM": OneClassSVM(nu=0.01, kernel="rbf", gamma="scale"),
        }
        self.fitted_models = {}

    @staticmethod
    def _to01(arr: np.ndarray) -> np.ndarray:
        arr = arr.astype(float)
        lo = np.min(arr)
        hi = np.max(arr)
        denom = max(1e-12, (hi - lo))
        return (arr - lo) / denom

    def fit(self):
        print(f"Training IsolationForest on {len(self.data_scaled)} rows...")
        self.models["IsolationForest"].fit(self.data_scaled)
        self.fitted_models["IsolationForest"] = self.models["IsolationForest"]

        print(f"Training OneClassSVM on subsample of {len(self.svm_data_scaled)} rows...")
        self.models["OneClassSVM"].fit(self.svm_data_scaled)
        self.fitted_models["OneClassSVM"] = self.models["OneClassSVM"]

    def get_if_svm_scores(self, normalize: bool = True):
        if "IsolationForest" not in self.fitted_models or "OneClassSVM" not in self.fitted_models:
            raise RuntimeError("Models not fitted. Call fit() first.")

        s_if = -self.fitted_models["IsolationForest"].decision_function(self.data_scaled)
        s_svm = -self.fitted_models["OneClassSVM"].decision_function(self.data_scaled)

        if normalize:
            return self._to01(s_if), self._to01(s_svm)
        return s_if, s_svm

    def predict(self):
        s_if01, s_svm01 = self.get_if_svm_scores(normalize=True)
        ml_score = 0.5 * (s_if01 + s_svm01)

        results = []
        for idx, score in enumerate(ml_score):
            results.append({
                "transaction_id": int(idx),
                "anomaly_score": float(score)
            })
        return results

    def train_xgboost(self):
        try:
            from xgboost import XGBClassifier
        except ImportError:
            print("XGBoost not installed. To enable supervised: pip install xgboost")
            return None

        if self.label_col not in self.data.columns:
            print(f"'{self.label_col}' not in dataset. Skipping supervised training.")
            return None

        X = self.features.values
        y = self.data[self.label_col].values
        model = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=42,
        )
        print(f"Training XGBoost on {len(self.data)} rows...")
        model.fit(X, y)
        self.fitted_models["XGBoost"] = model
        print("XGBoost trained.")
        return model

    def add_risk_scores(self, results):
        if "XGBoost" not in self.fitted_models or self.label_col not in self.data.columns:
            return results
        proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
        for i, row in enumerate(results):
            row["risk_score_baseline"] = float(proba[i])
        return results

    def explain(self, model_name="IsolationForest", sample_size=5000):
        if model_name not in self.fitted_models:
            raise ValueError(f"{model_name} not trained yet.")
        import shap  # noqa: F401

        n = self.data_scaled.shape[0]
        if n > sample_size:
            idx = np.random.RandomState(42).choice(n, size=sample_size, replace=False)
            data_for_shap = self.data_scaled[idx]
        else:
            data_for_shap = self.data_scaled

        explainer = shap.Explainer(self.fitted_models[model_name], data_for_shap)
        shap_values = explainer(data_for_shap)
        return shap_values

    def add_shap_explanations(self, results, model_name="IsolationForest", top_n=5, sample_size=5000):
        try:
            shap_values = self.explain(model_name=model_name, sample_size=sample_size)
        except Exception as e:
            print("SHAP explanation skipped:", e)
            for row in results:
                row["top_features"] = []
                row["explanation"] = {}
            return results

        for i, row in enumerate(results):
            if i < shap_values.values.shape[0]:
                sv = shap_values.values[i]
                top_idx = np.argsort(np.abs(sv))[-top_n:][::-1]
                row["top_features"] = [self.feature_names[j] for j in top_idx]
                row["explanation"] = {self.feature_names[j]: float(sv[j]) for j in top_idx}
            else:
                row["top_features"] = []
                row["explanation"] = {}
        return results

    def save_standardized_results(self, filename="models/anomaly_output_standard.json", model_name="IsolationForest"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        results = self.predict()
        results = self.add_risk_scores(results)
        results = self.add_shap_explanations(results, model_name=model_name)
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Standardized results saved to {filename}")

    def export_ml_scores_csv(self, out_path="models/ml_scores.csv", include_supervised=True, shap_top_n=5):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        s_if01, s_svm01 = self.get_if_svm_scores(normalize=True)
        ml_score = 0.5 * (s_if01 + s_svm01)

        # ✅ idx is in dataset
        idx_values = self.data["idx"].astype(int).values if "idx" in self.data.columns else np.arange(len(self.data), dtype=int)

        df_out = pd.DataFrame({
            "idx": idx_values,
            "model_if": s_if01,
            "model_svm": s_svm01,
            "ml_score": ml_score,
        })

        if include_supervised and "XGBoost" in self.fitted_models:
            proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
            df_out["ml_supervised"] = proba

            shap_str = ""
            try:
                if _HAS_SHAP:
                    import shap  # noqa: F401
                    expl = shap.TreeExplainer(self.fitted_models["XGBoost"])
                    sample_n = min(2000, len(self.features))
                    Xs = self.features.iloc[:sample_n].values
                    shap_vals = expl.shap_values(Xs)
                    mean_abs = np.abs(shap_vals).mean(axis=0)
                    top_idx = np.argsort(mean_abs)[-shap_top_n:][::-1]
                    top_names = [self.feature_names[i] for i in top_idx]
                    shap_str = ",".join(top_names)
            except Exception as e:
                print("Global SHAP top-features skipped:", e)

            df_out["shap_top_features"] = shap_str if shap_str else ""

        df_out.to_csv(out_path, index=False)
        print(f"✅ Wrote {out_path}")
