from knowledge.rules import infer_from_user_input

def test_rules_inference():
    payload = {
        "job": "Mechanic",
        "income_monthly": 13623846,
        "expense_monthly": 8517472,
        "debt_amount": 2843042,
        "late_payments_12m": 0,
        "credit_history_length_years": 10,
        "new_credit_accounts": 0,
        "credit_mix": "poor"
    }
    result = infer_from_user_input(payload)
    assert result["credit_score_class"] in {"good", "fair", "bad"}
