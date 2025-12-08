from knowledge.rule_engine import RuleEngine

def test_engine_basic():
    facts = {
        "income_expense_ratio": 1.9,
        "debt_ratio": 0.1,
        "late_payments_12m": 0,
        "credit_history_length_years": 6,
        "new_credit_accounts": 1,
        "credit_mix": "fair"
    }
    engine = RuleEngine()
    conclusions, fired = engine.infer(facts)
    assert conclusions.get("overall_risk") in {"low", "medium", "high"}
