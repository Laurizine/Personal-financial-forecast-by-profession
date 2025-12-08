from inference.bayesian_model import BayesianModel
from config.settings import DATASET_PATH

def test_train_and_predict():
    m = BayesianModel()
    m.train(DATASET_PATH)
    out = m.predict({
        "income_monthly": 13623846,
        "expense_monthly": 8517472,
        "debt_amount": 2843042,
        "late_payments_12m": 0,
        "credit_history_length_years": 10,
        "new_credit_accounts": 0,
        "credit_mix": "poor"
    })
    assert out["bayes_class"] in {"good", "fair", "bad"}
