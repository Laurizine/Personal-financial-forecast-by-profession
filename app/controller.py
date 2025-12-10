import math
import os
import time
import hashlib
import json
import logging
from knowledge.rule_engine import RuleEngine
from inference.bayesian_model import BayesianModel
from llm.explanation_service import generate_explanation
from app.database import DatabaseManager


# ================================
#  CONTROLLER CLASS
# ================================
class CreditController:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.bayes_model = BayesianModel()
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)

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

    def _make_cache_key(self, facts):
        model_name = os.environ.get("GEMINI_MODEL", "")
        fields = {
            "job": facts.get("job"),
            "income_monthly": facts.get("income_monthly"),
            "expense_monthly": facts.get("expense_monthly"),
            "debt_amount": facts.get("debt_amount"),
            "income_expense_ratio": facts.get("income_expense_ratio"),
            "debt_ratio": facts.get("debt_ratio"),
            "late_payments_12m": facts.get("late_payments_12m"),
            "credit_history_length_years": facts.get("credit_history_length_years"),
            "new_credit_accounts": facts.get("new_credit_accounts"),
            "credit_mix": facts.get("credit_mix"),
            "model": model_name,
        }
        s = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        h = hashlib.sha256(s.encode("utf-8")).hexdigest()
        return h

    def _get_cached_explanation(self, key):
        return self.db.get_cached_explanation(key)

    def _set_cached_explanation(self, key, value):
        self.db.save_cached_explanation(key, value)

    # ---------------------------------------
    #  HÀM XỬ LÝ CHÍNH
    #----------------------------------------
    def process(self, payload):
        start_time = time.time()
        # (1) Chuẩn hóa input → facts
        facts = self.build_facts(payload)
        try:
            self.logger.debug(f"facts summary: job={facts.get('job')}, income={facts.get('income_monthly')}, expense={facts.get('expense_monthly')}, debt={facts.get('debt_amount')}")
        except Exception:
            pass

        # (2) Chạy Rule Engine
        rule_conclusions, fired_rules = self.rule_engine.infer(facts)
        try:
            self.logger.debug(f"rules fired: count={len(fired_rules)}")
        except Exception:
            pass

        # Gom tri thức vào một dictionary
        reasoning_info = {
            "facts": facts,
            "rule_conclusions": rule_conclusions,
            "fired_rules": fired_rules
        }

        # (3) Chạy Bayesian Model
        bayes_output = self.bayes_model.predict(facts)
        try:
            self.logger.debug(f"bayes: class={bayes_output.get('bayes_class')}, score={bayes_output.get('bayes_score')}, conf={bayes_output.get('confidence')}")
        except Exception:
            pass

        # (4) Tổng hợp kết quả cuối
        final_class = self.resolve_final_class(rule_conclusions, bayes_output)
        try:
            self.logger.info(f"final_class={final_class}")
        except Exception:
            pass

        key = self._make_cache_key(facts)
        cached = self._get_cached_explanation(key)
        if cached is not None:
            explanation = cached
        else:
            try:
                explanation = generate_explanation(
                    facts=facts,
                    rule_conclusions=rule_conclusions,
                    bayes_output=bayes_output,
                    fired_rules=fired_rules,
                    final_class=final_class
                )
                self._set_cached_explanation(key, explanation)
            except Exception as e:
                explanation = f"Lỗi Gemini: {str(e)}"

        # (6) Trả về kết quả cho UI
        result_dict = {
            "facts": facts,
            "rule_conclusions": rule_conclusions,
            "fired_rules": fired_rules,
            "bayesian": bayes_output,
            "final_class": final_class,
            "llm_explanation": explanation
        }
        
        # (7) Log vào DB
        duration = time.time() - start_time
        self.db.log_prediction(facts, result_dict, duration)
        
        return result_dict

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
