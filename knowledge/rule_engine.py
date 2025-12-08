from knowledge.rules import rules

class RuleEngine:
    def __init__(self):
        self.rules = rules

    def infer(self, facts):
        """
        facts: dict dữ liệu ban đầu (user input + tỷ lệ đã tính)
        return:
            conclusions: kết luận suy diễn được
            fired_rules: các luật đã kích hoạt
        """

        # Working memory = facts ban đầu
        wm = facts.copy()

        conclusions = {}
        fired_rules = []
        updated = True  # kiểm tra có luật nào kích hoạt nữa không

        while updated:
            updated = False

            for rule in self.rules:
                rule_name = rule["name"]
                condition = rule["condition"]
                conclusion_key, conclusion_value = rule["conclusion"]

                # Nếu luật chưa kích hoạt trước đó
                if rule_name not in fired_rules:
                    try:
                        # Nếu điều kiện đúng
                        if condition(wm):
                            # Ghi nhận kết luận
                            wm[conclusion_key] = conclusion_value
                            conclusions[conclusion_key] = conclusion_value

                            # Đánh dấu luật đã kích hoạt
                            fired_rules.append(rule_name)

                            # Cho biết working memory thay đổi → lặp lại
                            updated = True

                    except Exception as e:
                        print(f"Lỗi đánh giá rule {rule_name}: {e}")

        return conclusions, fired_rules



# Demo test nhanh
if __name__ == "__main__":
    sample_facts = {
        "income_expense_ratio": 1.9,
        "debt_ratio": 0.1,
        "late_payments_12m": 0,
        "credit_history_length_years": 6,
        "new_credit_accounts": 1,
        "credit_mix": "fair"
    }

    engine = RuleEngine()
    conclusions, fired_rules = engine.infer(sample_facts)

    print("=== KẾT LUẬN SUY DIỄN ===")
    print(conclusions)

    print("\n=== RULE KÍCH HOẠT ===")
    print(fired_rules)
