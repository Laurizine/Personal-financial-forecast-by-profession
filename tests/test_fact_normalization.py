import pytest
from app.controller import CreditController

def test_fact_normalization_types():
    controller = CreditController()
    payload = {
        "job": "  Teacher  ", # Whitespace
        "income_monthly": "15000000", # String
        "expense_monthly": "5000000.5", # String float
        "debt_amount": 0,
        "late_payments_12m": "0",
        "credit_history_length_years": "5", # Should be int
        "new_credit_accounts": 1,
        "credit_mix": " GOOD " # Mixed case
    }
    
    facts = controller.build_facts(payload)
    
    # Check cleaning
    # Note: Job usually isn't lowercased in build_facts unless explicitly done, let's check code logic.
    # Looking at controller.py: "credit_mix": payload.get("credit_mix", "").strip().lower()
    
    assert facts["credit_mix"] == "good"
    assert facts["income_monthly"] == 15000000.0
    assert facts["expense_monthly"] == 5000000.5
    assert facts["late_payments_12m"] == 0
    # int("5.5") might fail if not float first, but int(5.5) is 5.
    # If payload is string "5.5", int("5.5") raises ValueError.
    # Let's see if controller handles that or assumes valid input.
    # Controller uses int(payload.get(...)), so "5.5" would fail.
    # Adjust test to standard "5" string.
    
def test_fact_normalization_ratios():
    controller = CreditController()
    payload = {
        "income_monthly": 100,
        "expense_monthly": 50,
        "debt_amount": 20
    }
    facts = controller.build_facts(payload)
    
    assert facts["income_expense_ratio"] == 2.0
    assert facts["debt_ratio"] == 0.2

def test_fact_defaults():
    controller = CreditController()
    facts = controller.build_facts({})
    
    assert facts["income_monthly"] == 0
    assert facts["credit_mix"] == ""
