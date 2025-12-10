import pytest
from app.controller import CreditController

def test_controller_end_to_end():
    """
    Kiểm thử luồng đi từ input -> build_facts -> rules -> bayes -> llm (mocked or real) -> result
    """
    controller = CreditController()
    
    payload = {
        "job": "Engineer",
        "income_monthly": 20000000,
        "expense_monthly": 10000000,
        "debt_amount": 5000000,
        "late_payments_12m": 0,
        "credit_history_length_years": 5,
        "new_credit_accounts": 1,
        "credit_mix": "good"
    }
    
    # Run process
    result = controller.process(payload)
    
    # Assert keys exist
    assert "facts" in result
    assert "rule_conclusions" in result
    assert "fired_rules" in result
    assert "bayesian" in result
    assert "final_class" in result
    assert "llm_explanation" in result
    
    # Assert logical consistency
    # Income 20m, expense 10m -> ratio 2.0 -> good
    assert result["facts"]["income_monthly"] == 20000000
    assert result["facts"]["income_expense_ratio"] == 2.0
    
    # Final class should be reasonable
    assert result["final_class"] in ["good", "fair", "bad"]
