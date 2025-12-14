def _filled_value(v):
    if v is None:
        return False
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return v.strip() != ""
    return True

def build_causal_dot(result):
    facts = result.get("facts", {}) or {}
    rc = result.get("rule_conclusions", {}) or {}
    final_class = result.get("final_class", "") or ""

    fact_nodes = [
        "income_monthly",
        "expense_monthly",
        "debt_amount",
        "late_payments_12m",
        "credit_history_length_years",
        "new_credit_accounts",
        "credit_mix",
    ]
    derived = ["income_expense_ratio", "debt_ratio"]
    intermediate = [
        "financial_capacity",
        "debt_risk",
        "payment_behavior",
        "credit_history_quality",
        "newcredit_risk",
        "credit_mix_quality",
    ]
    end_nodes = ["overall_risk", "rule_credit_class"]

    lines = []
    lines.append("digraph {")
    lines.append("rankdir=LR;")
    lines.append("node [shape=box];")

    for n in fact_nodes:
        filled = _filled_value(facts.get(n))
        if filled:
            lines.append(f'{n} [label="{n}", style=filled, fillcolor="#FFD54F"];')
        else:
            lines.append(f'{n} [label="{n}"];')

    for n in derived:
        filled = _filled_value(facts.get(n))
        if filled:
            lines.append(f'{n} [label="{n}", style=filled, fillcolor="#FFECB3"];')
        else:
            lines.append(f'{n} [label="{n}"];')

    for n in intermediate:
        filled = _filled_value(rc.get(n))
        if filled:
            lines.append(f'{n} [label="{n}", style=filled, fillcolor="#AED581"];')
        else:
            lines.append(f'{n} [label="{n}"];')

    for n in end_nodes:
        filled = _filled_value(rc.get(n))
        if filled:
            lines.append(f'{n} [label="{n}", style=filled, fillcolor="#81C784"];')
        else:
            lines.append(f'{n} [label="{n}"];')

    lines.append('final_class [label="final_class", shape=doubleoctagon, style=filled, fillcolor="#EF6C00"];')

    lines.append("income_monthly -> income_expense_ratio;")
    lines.append("expense_monthly -> income_expense_ratio;")
    lines.append("income_expense_ratio -> financial_capacity;")

    lines.append("debt_amount -> debt_ratio;")
    lines.append("income_monthly -> debt_ratio;")
    lines.append("debt_ratio -> debt_risk;")

    lines.append("late_payments_12m -> payment_behavior;")
    lines.append("credit_history_length_years -> credit_history_quality;")
    lines.append("new_credit_accounts -> newcredit_risk;")
    lines.append("credit_mix -> credit_mix_quality;")

    lines.append("financial_capacity -> overall_risk;")
    lines.append("debt_risk -> overall_risk;")
    lines.append("payment_behavior -> overall_risk;")
    lines.append("credit_history_quality -> overall_risk;")
    lines.append("newcredit_risk -> overall_risk;")
    lines.append("credit_mix_quality -> overall_risk;")

    lines.append("overall_risk -> rule_credit_class -> final_class;")
    lines.append("}")

    return "\n".join(lines)
