rules = [
    {"name": "R1_income_strong", "condition": lambda f: f.get("income_expense_ratio", 0) >= 1.8, "conclusion": ("financial_capacity", "strong")},
    {"name": "R2_income_stable", "condition": lambda f: 1.3 <= f.get("income_expense_ratio", 0) < 1.8, "conclusion": ("financial_capacity", "stable")},
    {"name": "R3_income_weak", "condition": lambda f: f.get("income_expense_ratio", 0) < 1.3, "conclusion": ("financial_capacity", "weak")},
    {"name": "R4_debt_low", "condition": lambda f: f.get("debt_ratio", 1) < 0.2, "conclusion": ("debt_risk", "low")},
    {"name": "R5_debt_medium", "condition": lambda f: 0.2 <= f.get("debt_ratio", 1) <= 0.6, "conclusion": ("debt_risk", "medium")},
    {"name": "R6_debt_high", "condition": lambda f: f.get("debt_ratio", 0) > 0.6, "conclusion": ("debt_risk", "high")},
    {"name": "R7_no_late", "condition": lambda f: int(f.get("late_payments_12m", 0)) == 0, "conclusion": ("payment_behavior", "excellent")},
    {"name": "R8_few_late", "condition": lambda f: 1 <= int(f.get("late_payments_12m", 0)) <= 2, "conclusion": ("payment_behavior", "average")},
    {"name": "R9_many_late", "condition": lambda f: int(f.get("late_payments_12m", 0)) >= 3, "conclusion": ("payment_behavior", "poor")},
    {"name": "R10_history_strong", "condition": lambda f: int(f.get("credit_history_length_years", 0)) >= 10, "conclusion": ("credit_history_quality", "strong")},
    {"name": "R11_history_medium", "condition": lambda f: 5 <= int(f.get("credit_history_length_years", 0)) < 10, "conclusion": ("credit_history_quality", "medium")},
    {"name": "R12_history_weak", "condition": lambda f: int(f.get("credit_history_length_years", 0)) < 5, "conclusion": ("credit_history_quality", "weak")},
    {"name": "R13_newcredit_low", "condition": lambda f: int(f.get("new_credit_accounts", 0)) == 0, "conclusion": ("newcredit_risk", "low")},
    {"name": "R14_newcredit_medium", "condition": lambda f: 1 <= int(f.get("new_credit_accounts", 0)) <= 2, "conclusion": ("newcredit_risk", "medium")},
    {"name": "R15_newcredit_high", "condition": lambda f: int(f.get("new_credit_accounts", 0)) >= 3, "conclusion": ("newcredit_risk", "high")},
    {"name": "R16_mix_good", "condition": lambda f: str(f.get("credit_mix", "")).lower() == "good", "conclusion": ("credit_mix_quality", "diverse")},
    {"name": "R17_mix_fair", "condition": lambda f: str(f.get("credit_mix", "")).lower() == "fair", "conclusion": ("credit_mix_quality", "balanced")},
    {"name": "R18_mix_poor", "condition": lambda f: str(f.get("credit_mix", "")).lower() == "poor", "conclusion": ("credit_mix_quality", "limited")},
    {"name": "R19_highrisk_combination", "condition": lambda f: f.get("payment_behavior") == "poor" or f.get("debt_risk") == "high", "conclusion": ("overall_risk", "high")},
    {"name": "R20_mediumrisk_combination", "condition": lambda f: f.get("payment_behavior") == "average" or f.get("debt_risk") == "medium", "conclusion": ("overall_risk", "medium")},
    {"name": "R21_lowrisk_combination", "condition": lambda f: f.get("payment_behavior") == "excellent" and f.get("debt_risk") == "low" and f.get("financial_capacity") in ("strong", "stable"), "conclusion": ("overall_risk", "low")},
    {"name": "R22_suggest_good", "condition": lambda f: f.get("overall_risk") == "low", "conclusion": ("rule_credit_class", "good")},
    {"name": "R23_suggest_fair", "condition": lambda f: f.get("overall_risk") == "medium", "conclusion": ("rule_credit_class", "fair")},
    {"name": "R24_suggest_bad", "condition": lambda f: f.get("overall_risk") == "high", "conclusion": ("rule_credit_class", "bad")},
    {"name": "R25_score_good", "condition": lambda f: int(f.get("credit_score", 0)) >= 750, "conclusion": ("rule_credit_class", "good")},
    {"name": "R26_score_fair", "condition": lambda f: int(f.get("credit_score", 0)) >= 655 and f.get("debt_ratio", 1) <= 0.4, "conclusion": ("rule_credit_class", "fair")},
    {"name": "R27_score_bad", "condition": lambda f: int(f.get("credit_score", 1000)) < 500 and f.get("debt_ratio", 0) >= 0.6, "conclusion": ("rule_credit_class", "bad")},
]

def _safe_ratio(a, b):
    return a / (b if b and b > 0 else 1)

def apply_rules(facts):
    facts = dict(facts)
    fired = []
    changed = True
    while changed:
        changed = False
        for r in rules:
            try:
                if r["condition"](facts):
                    k, v = r["conclusion"]
                    if facts.get(k) != v:
                        facts[k] = v
                        fired.append(r["name"])
                        changed = True
            except Exception:
                pass
    return facts, fired

def infer_from_user_input(payload):
    job = payload.get("job")
    income = int(payload.get("income_monthly", 0) or 0)
    expense = int(payload.get("expense_monthly", 0) or 0)
    debt = int(payload.get("debt_amount", 0) or 0)
    late = int(payload.get("late_payments_12m", 0) or 0)
    history = int(payload.get("credit_history_length_years", 0) or 0)
    new_acc = int(payload.get("new_credit_accounts", 0) or 0)
    mix = str(payload.get("credit_mix", "")).strip().lower()
    score = payload.get("credit_score", None)
    score = int(score) if score is not None and score != "" else None

    ier = round(_safe_ratio(income, expense), 2)
    dr = round(_safe_ratio(debt, income), 2)

    base = {
        "job": job,
        "income_monthly": income,
        "expense_monthly": expense,
        "debt_amount": debt,
        "late_payments_12m": late,
        "credit_history_length_years": history,
        "new_credit_accounts": new_acc,
        "credit_mix": mix,
        "credit_score": score if score is not None else 0,
        "income_expense_ratio": ier,
        "debt_ratio": dr,
    }

    facts, fired = apply_rules(base)

    cls = facts.get("rule_credit_class")
    if not cls:
        risk = facts.get("overall_risk")
        if risk == "low":
            cls = "good"
        elif risk == "medium":
            cls = "fair"
        else:
            cls = "bad"

    return {
        "credit_score_class": cls,
        "overall_risk": facts.get("overall_risk"),
        "metrics": {"income_expense_ratio": ier, "debt_ratio": dr},
        "fired_rules": fired,
        "facts": facts,
    }

def _mix(x):
    return str(x).strip().lower()

def _safe_ratio(a, b):
    return a / (b if b and b > 0 else 1)

def apply_rules(facts):
    facts = dict(facts)
    fired = []
    changed = True
    while changed:
        changed = False
        for r in rules:
            try:
                if r["condition"](facts):
                    k, v = r["conclusion"]
                    if facts.get(k) != v:
                        facts[k] = v
                        fired.append(r["name"])
                        changed = True
            except Exception:
                pass
    return facts, fired

def infer_from_user_input(payload):
    job = payload.get("job")
    income = int(payload.get("income_monthly", 0) or 0)
    expense = int(payload.get("expense_monthly", 0) or 0)
    debt = int(payload.get("debt_amount", 0) or 0)
    late = int(payload.get("late_payments_12m", 0) or 0)
    history = int(payload.get("credit_history_length_years", 0) or 0)
    new_acc = int(payload.get("new_credit_accounts", 0) or 0)
    mix = _mix(payload.get("credit_mix", ""))
    score = payload.get("credit_score", None)
    score = int(score) if score is not None and score != "" else None

    ier = round(_safe_ratio(income, expense), 2)
    dr = round(_safe_ratio(debt, income), 2)

    base = {
        "job": job,
        "income_monthly": income,
        "expense_monthly": expense,
        "debt_amount": debt,
        "late_payments_12m": late,
        "credit_history_length_years": history,
        "new_credit_accounts": new_acc,
        "credit_mix": mix,
        "income_expense_ratio": ier,
        "debt_ratio": dr,
    }

    facts, fired = apply_rules(base)

    cls = facts.get("rule_credit_class")
    if not cls:
        risk = facts.get("overall_risk")
        if risk == "low":
            cls = "good"
        elif risk == "medium":
            cls = "fair"
        else:
            cls = "bad"

    return {
        "credit_score_class": cls,
        "overall_risk": facts.get("overall_risk"),
        "metrics": {"income_expense_ratio": ier, "debt_ratio": dr},
        "fired_rules": fired,
        "facts": facts,
    }
