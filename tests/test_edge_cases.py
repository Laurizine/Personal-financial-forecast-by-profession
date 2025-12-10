import pytest
from app.controller import CreditController

def test_zero_values():
    controller = CreditController()
    payload = {
        "income_monthly": 0,
        "expense_monthly": 0,
        "debt_amount": 0
    }
    # Should not crash
    result = controller.process(payload)
    facts = result["facts"]
    
    # Division by zero handled safely
    assert facts["income_expense_ratio"] == 0.0
    assert facts["debt_ratio"] == 0.0

def test_missing_keys():
    controller = CreditController()
    payload = {} # Empty
    
    result = controller.process(payload)
    facts = result["facts"]
    
    # Check defaults
    assert facts["income_monthly"] == 0.0
    assert facts["late_payments_12m"] == 0

def test_extreme_values():
    controller = CreditController()
    payload = {
        "income_monthly": 1e9, # 1 billion
        "expense_monthly": 1e9,
        "debt_amount": 1e12 # 1 trillion
    }
    
    result = controller.process(payload)
    # Just ensure it finishes
    assert result["final_class"] in ["good", "fair", "bad"]
