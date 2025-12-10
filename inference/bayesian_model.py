import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
import os
from config.settings import MODEL_PATH
import logging

logger = logging.getLogger(__name__)


class BayesianModel:
    def __init__(self, model_path=None):
        self.model_path = model_path or MODEL_PATH
        self.pipeline = None

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
        y = df["credit_score_class"]

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
        model = GaussianNB()

        # Final pipeline
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", model)
        ])

        # Train
        pipeline.fit(X, y)

        # Save pipeline to file
        with open(self.model_path, "wb") as f:
            pickle.dump(pipeline, f)

        # Load pipeline in RAM
        self.pipeline = pipeline

        logger.info("BayesianModel training completed and model saved")
        logger.info("BayesianModel pipeline loaded into memory after training")


    # =====================================================
    # LOAD MODEL
    # =====================================================
    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.pipeline = pickle.load(f)
        logger.info(f"BayesianModel loaded from file: path={self.model_path}")


    # =====================================================
    # PREDICT FUNCTION
    # =====================================================
    def predict(self, facts):

        if self.pipeline is None:
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
        credit_class = self.pipeline.predict(input_df)[0]

        # Predict probability
        probs = self.pipeline.predict_proba(input_df)[0]
        class_idx = list(self.pipeline.classes_).index(credit_class)
        confidence = probs[class_idx]

        # Convert to FICO-like score
        score = self.estimate_score(credit_class, confidence)

        return {
            "bayes_class": str(credit_class),
            "confidence": float(confidence),
            "bayes_score": score
        }


    # =====================================================
    # SCORE CONVERSION
    # =====================================================
    def estimate_score(self, cls, conf):
        if cls == "good":
            return int(700 + conf * 70)
        elif cls == "fair":
            return int(640 + conf * 50)
        else:
            return int(500 + conf * 130)


# =====================================================
# TRAIN WHEN RUN DIRECTLY
# =====================================================
if __name__ == "__main__":
    model = BayesianModel()
    from config.settings import DATASET_PATH
    model.train(DATASET_PATH)
