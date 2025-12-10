import pytest
import numpy as np
from inference.bayesian_model import BayesianModel

@pytest.fixture
def bayes_model():
    return BayesianModel()

def test_bayes_prediction_stability(bayes_model):
    # Ensure repeated calls with same input give same output
    facts = {
        "income_monthly": 15000000,
        "expense_monthly": 8000000,
        "debt_amount": 2000000,
        "late_payments_12m": 0,
        "credit_history_length_years": 5,
        "new_credit_accounts": 1,
        "credit_mix": "fair"
    }
    
    res1 = bayes_model.predict(facts)
    res2 = bayes_model.predict(facts)
    
    assert res1["bayes_class"] == res2["bayes_class"]
    assert res1["confidence"] == res2["confidence"]

def test_bayes_outliers(bayes_model):
    # Very high income, zero debt
    facts = {
        "income_monthly": 10**9,
        "expense_monthly": 10**6,
        "debt_amount": 0,
        "late_payments_12m": 0,
        "credit_history_length_years": 20,
        "new_credit_accounts": 0,
        "credit_mix": "good"
    }
    
    res = bayes_model.predict(facts)
    # Should likely be good
    assert res["bayes_class"] == "good"
    
def test_bayes_negative_input(bayes_model):
    # Negative income (physically impossible but model shouldn't crash)
    facts = {
        "income_monthly": -5000000,
        "expense_monthly": 5000000,
        "debt_amount": 0,
        "late_payments_12m": 0,
        "credit_history_length_years": 0,
        "new_credit_accounts": 0,
        "credit_mix": "poor"
    }
    
    try:
        res = bayes_model.predict(facts)
        assert "bayes_class" in res
    except Exception as e:
        pytest.fail(f"Bayesian model crashed on negative input: {e}")
