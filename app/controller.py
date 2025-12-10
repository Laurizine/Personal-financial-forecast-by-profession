import math
from knowledge.rule_engine import RuleEngine
from inference.bayesian_model import BayesianModel
from llm.explanation_service import generate_explanation


# ================================
#  CONTROLLER CLASS
# ================================
class CreditController:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.bayes_model = BayesianModel()

    # ---------------------------------------
    #  TÍNH TỶ LỆ AN TOÀN
    # ---------------------------------------
    def _safe_ratio(self, a, b):
        try:
            return a / b if b and b > 0 else 0.0
        except:
            return 0.0

    # ---------------------------------------
    # TIỀN XỬ LÝ INPUT TỪ FORM
    # ---------------------------------------
    def build_facts(self, payload):
        income = float(payload.get("income_monthly", 0))
        expense = float(payload.get("expense_monthly", 0))
        debt = float(payload.get("debt_amount", 0))

        facts = {
            "job": payload.get("job"),
            "income_monthly": income,
            "expense_monthly": expense,
            "debt_amount": debt,
            "late_payments_12m": int(payload.get("late_payments_12m", 0)),
            "credit_history_length_years": int(payload.get("credit_history_length_years", 0)),
            "new_credit_accounts": int(payload.get("new_credit_accounts", 0)),
            "credit_mix": payload.get("credit_mix", "").strip().lower(),

            # Tính thêm các tỷ lệ
            "income_expense_ratio": round(self._safe_ratio(income, expense), 2),
            "debt_ratio": round(self._safe_ratio(debt, income), 2),
        }

        return facts

    # ---------------------------------------
    #  HÀM XỬ LÝ CHÍNH
    #----------------------------------------
    def process(self, payload):
        # (1) Chuẩn hóa input → facts
        facts = self.build_facts(payload)

        # (2) Chạy Rule Engine
        rule_conclusions, fired_rules = self.rule_engine.infer(facts)

        # Gom tri thức vào một dictionary
        reasoning_info = {
            "facts": facts,
            "rule_conclusions": rule_conclusions,
            "fired_rules": fired_rules
        }

        # (3) Chạy Bayesian Model
        bayes_output = self.bayes_model.predict(facts)

        # (4) Tổng hợp kết quả cuối
        final_class = self.resolve_final_class(rule_conclusions, bayes_output)

        # (5) Sinh giải thích bằng LLM
        try:
            explanation = generate_explanation(
                facts=facts,
                rule_conclusions=rule_conclusions,
                bayes_output=bayes_output,
                fired_rules=fired_rules,
                final_class=final_class
            )
        except Exception as e:
            explanation = f"Lỗi Gemini: {str(e)}"

        # (6) Trả về kết quả cho UI
        return {
            "facts": facts,
            "rule_conclusions": rule_conclusions,
            "fired_rules": fired_rules,
            "bayesian": bayes_output,
            "final_class": final_class,
            "llm_explanation": explanation
        }

    # ---------------------------------------
    # GHÉP KẾT QUẢ RULE + BAYES
    # ---------------------------------------
    def resolve_final_class(self, rule_conclusions, bayes_output):
        # Nếu Rule Engine đã có rule_credit_class → ưu tiên
        if "rule_credit_class" in rule_conclusions:
            return rule_conclusions["rule_credit_class"]

        # Nếu không có thì dùng Bayesian
        return bayes_output.get("bayes_class", "unknown")


# ================================
#  TEST CONTROLLER
# ================================
if __name__ == "__main__":
    controller = CreditController()

    sample_input = {
        "job": "IT Engineer",
        "income_monthly": 20000000,
        "expense_monthly": 12000000,
        "debt_amount": 6000000,
        "late_payments_12m": 1,
        "credit_history_length_years": 6,
        "new_credit_accounts": 2,
        "credit_mix": "fair"
    }

    result = controller.process(sample_input)
    print(result)
