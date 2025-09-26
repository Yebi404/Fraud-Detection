import os
import json
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

try:
    import shap  # noqa: F401
    _HAS_SHAP = True
except Exception:
    _HAS_SHAP = False


class AnomalyDetector:
    def __init__(self, data: pd.DataFrame, target_column: str = "isFraud", svm_sample_size: int = 10000):
        self.data = data.copy()
        self.target_column = target_column if target_column in self.data.columns else None

        self.features = (
            self.data.drop(columns=[self.target_column], errors="ignore")
            if self.target_column
            else self.data
        )
        self.features = pd.get_dummies(self.features, drop_first=True)
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
                contamination=0.02, n_jobs=-1, random_state=42
            ),
            "OneClassSVM": OneClassSVM(nu=0.02, kernel="rbf", gamma="scale"),
        }
        self.fitted_models = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    @staticmethod
    def _to01(arr: np.ndarray) -> np.ndarray:
        arr = arr.astype(float)
        lo = np.min(arr)
        hi = np.max(arr)
        denom = max(1e-12, (hi - lo))
        return (arr - lo) / denom

    def fit(self):
        self.models["IsolationForest"].fit(self.data_scaled)
        self.fitted_models["IsolationForest"] = self.models["IsolationForest"]

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
        ml_score = 0.4 * s_if01 + 0.4 * s_svm01

        if "XGBoost" in self.fitted_models:
            proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
            ml_score += 0.2 * proba

        ml_score = self._to01(ml_score)

        results = []
        for idx, score in enumerate(ml_score):
            results.append({
                "transaction_id": int(idx),
                "anomaly_score": float(score)
            })
        return results

    def train_xgboost(self):
        if self.target_column is None:
            return None
        try:
            from xgboost import XGBClassifier
        except ImportError:
            return None

        X = self.features.values
        y = self.data[self.target_column].values

        # ===== TRAIN / TEST SPLIT =====
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=42,
        )
        model.fit(self.X_train, self.y_train)
        self.fitted_models["XGBoost"] = model

        # Store predictions for all data so ml_score CSV stays same format
        proba = model.predict_proba(X)[:, 1]
        self.data["ml_score"] = proba

        return model

    def evaluate_model(self):
        if self.X_test is None or self.y_test is None or "XGBoost" not in self.fitted_models:
            print("No test data or model found for evaluation.")
            return

        y_pred = self.fitted_models["XGBoost"].predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, zero_division=0)
        recall = recall_score(self.y_test, y_pred, zero_division=0)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)

        print("\n--- Model Evaluation Metrics ---")
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1-Score : {f1:.4f}")
        print("--------------------------------")

    def add_risk_scores(self, results):
        if "XGBoost" not in self.fitted_models or self.target_column is None:
            return results
        proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
        for i, row in enumerate(results):
            row["risk_score_baseline"] = float(proba[i])
        return results

    def explain(self, model_name="IsolationForest", sample_size=5000):
        if model_name not in self.fitted_models:
            raise ValueError(f"{model_name} not trained yet.")
        import shap
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
        except Exception:
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

    def export_ml_scores_csv(self, out_path="models/ml_scores.csv", include_supervised=True, shap_top_n=5):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        s_if01, s_svm01 = self.get_if_svm_scores(normalize=True)
        ml_score = 0.4 * s_if01 + 0.4 * s_svm01

        if "XGBoost" in self.fitted_models and self.target_column is not None:
            proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
            ml_score += 0.2 * proba

        ml_score = self._to01(ml_score)

        if "idx" in self.data.columns:
            idx_values = self.data["idx"].astype(int).values
        else:
            idx_values = np.arange(len(self.data), dtype=int)

        df_out = pd.DataFrame({
            "idx": idx_values,
            "model_if": s_if01,
            "model_svm": s_svm01,
            "ml_score": ml_score,
        })

        if include_supervised and "XGBoost" in self.fitted_models and self.target_column is not None:
            proba = self.fitted_models["XGBoost"].predict_proba(self.features.values)[:, 1]
            df_out["ml_supervised"] = proba

            shap_str = ""
            try:
                if _HAS_SHAP:
                    import shap
                    expl = shap.TreeExplainer(self.fitted_models["XGBoost"])
                    sample_n = min(2000, len(self.features))
                    Xs = self.features.iloc[:sample_n].values
                    shap_vals = expl.shap_values(Xs)
                    mean_abs = np.abs(shap_vals).mean(axis=0)
                    top_idx = np.argsort(mean_abs)[-shap_top_n:][::-1]
                    top_names = [self.feature_names[i] for i in top_idx]
                    shap_str = ",".join(top_names)
            except Exception:
                pass
            df_out["shap_top_features"] = shap_str if shap_str else ""

        df_out.to_csv(out_path, index=False)

