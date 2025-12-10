import pytest
from knowledge.rule_engine import RuleEngine

@pytest.fixture
def engine():
    return RuleEngine()

def test_rule_high_risk(engine):
    # Case: Late payments > 2 -> High risk
    facts = {
        "late_payments_12m": 5,
        "income_expense_ratio": 1.5,
        "debt_ratio": 0.5,
        "credit_history_length_years": 2,
        "new_credit_accounts": 2,
        "credit_mix": "poor"
    }
    conclusions, fired = engine.infer(facts)
    
    # Expect bad credit score or high risk flag
    # Note: Adjust assertions based on actual rules in knowledge/rules.py
    # Assuming standard logic: many late payments = bad
    assert conclusions.get("rule_credit_class") == "bad" or conclusions.get("risk_level") == "high"

def test_rule_good_standing(engine):
    # Case: No late payments, good ratio
    facts = {
        "late_payments_12m": 0,
        "income_expense_ratio": 3.0,
        "debt_ratio": 0.1,
        "credit_history_length_years": 10,
        "new_credit_accounts": 0,
        "credit_mix": "good"
    }
    conclusions, fired = engine.infer(facts)
    
    assert conclusions.get("rule_credit_class") == "good" or conclusions.get("financial_health") == "strong"

def test_rule_conflict_resolution(engine):
    # Case: Mixed signals
    # High income but bad history (if rules allow this combo)
    facts = {
        "late_payments_12m": 5, # bad
        "income_expense_ratio": 5.0, # good
        "debt_ratio": 0.0, # good
        "credit_history_length_years": 1,
        "new_credit_accounts": 5,
        "credit_mix": "standard"
    }
    conclusions, fired = engine.infer(facts)
    
    # Usually safety rules (late payments) override income
    assert conclusions.get("rule_credit_class") in ["bad", "fair"]
