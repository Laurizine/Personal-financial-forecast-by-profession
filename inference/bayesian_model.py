import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import BayesianRidge
from sklearn.pipeline import Pipeline
import os
from config.settings import MODEL_PATH
import logging

logger = logging.getLogger(__name__)


class BayesianModel:
    def __init__(self, model_path=None):
        self.model_path = model_path or MODEL_PATH
        self.pipeline = None
        self.pipeline_cls = None
        self.pipeline_reg = None

        # Chỉ load nếu file model đã tồn tại
        if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 0:
            try:
                self.load_model()
                logger.info(f"BayesianModel loaded: path={self.model_path}")
            except Exception as e:
                logger.error(f"BayesianModel load failed: {e}")
                logger.info("Please retrain the model.")
        else:
            logger.info("No existing model found. Train first to generate model.pkl.")


    # =====================================================
    # TRAINING MODEL
    # =====================================================
    def train(self, dataset_path):
        df = pd.read_csv(dataset_path)

        # Features used for prediction
        feature_cols = [
            "income_monthly",
            "expense_monthly",
            "debt_amount",
            "late_payments_12m",
            "credit_history_length_years",
            "new_credit_accounts",
            "credit_mix",
            "income_expense_ratio",
            "debt_ratio"
        ]

        X = df[feature_cols]
        y_cls = df["credit_score_class"]
        y_reg = df["credit_score"].astype(float)

        # Categorical + numerical columns
        cat_cols = ["credit_mix"]
        num_cols = [col for col in feature_cols if col not in cat_cols]

        # Preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
            ]
        )

        # Model (Naive Bayes – interpretable)
        model_cls = GaussianNB()
        model_reg = BayesianRidge()

        # Final pipeline
        pipeline_cls = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", model_cls)
        ])
        pipeline_reg = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model_reg)
        ])

        # Train
        pipeline_cls.fit(X, y_cls)
        pipeline_reg.fit(X, y_reg)

        # Save pipeline to file
        with open(self.model_path, "wb") as f:
            pickle.dump({"classifier": pipeline_cls, "regressor": pipeline_reg}, f)

        # Load pipeline in RAM
        self.pipeline_cls = pipeline_cls
        self.pipeline_reg = pipeline_reg

        logger.info("BayesianModel training completed and model saved")
        logger.info("BayesianModel pipeline loaded into memory after training")


    # =====================================================
    # LOAD MODEL
    # =====================================================
    def load_model(self):
        with open(self.model_path, "rb") as f:
            obj = pickle.load(f)
        if isinstance(obj, dict) and "classifier" in obj and "regressor" in obj:
            self.pipeline_cls = obj["classifier"]
            self.pipeline_reg = obj["regressor"]
        else:
            self.pipeline_cls = obj
            self.pipeline_reg = None
        logger.info(f"BayesianModel loaded from file: path={self.model_path}")


    # =====================================================
    # PREDICT FUNCTION
    # =====================================================
    def predict(self, facts):
        if self.pipeline_cls is None:
            raise Exception("Model not loaded or trained!")

        income = facts.get("income_monthly", 0)
        expense = facts.get("expense_monthly", 1)
        debt = facts.get("debt_amount", 0)

        ier = facts.get("income_expense_ratio", income / (expense if expense else 1))
        dr = facts.get("debt_ratio", debt / (income if income else 1))

        input_df = pd.DataFrame([{
            "income_monthly": income,
            "expense_monthly": expense,
            "debt_amount": debt,
            "late_payments_12m": facts.get("late_payments_12m", 0),
            "credit_history_length_years": facts.get("credit_history_length_years", 0),
            "new_credit_accounts": facts.get("new_credit_accounts", 0),
            "credit_mix": facts.get("credit_mix", "poor"),
            "income_expense_ratio": ier,
            "debt_ratio": dr
        }])

        # Predict class
        credit_class = self.pipeline_cls.predict(input_df)[0]

        # Predict probability
        probs = self.pipeline_cls.predict_proba(input_df)[0]
        class_idx = list(self.pipeline_cls.classes_).index(credit_class)
        confidence = probs[class_idx]

        # Convert to FICO-like score từ regressor
        if self.pipeline_reg is None:
            raise Exception("Score regressor not available. Please retrain the model.")
        pred_score = float(self.pipeline_reg.predict(input_df)[0])
        score = int(max(300, min(900, pred_score)))

        return {
            "bayes_class": str(credit_class),
            "confidence": float(confidence),
            "bayes_score": score
        }


    # (removed interpolation fallback)


# =====================================================
# TRAIN WHEN RUN DIRECTLY
# =====================================================
if __name__ == "__main__":
    model = BayesianModel()
    from config.settings import DATASET_PATH
    model.train(DATASET_PATH)
