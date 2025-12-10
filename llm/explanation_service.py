import json
import textwrap
import os
import time
import re
try:
    import google.generativeai as genai
except Exception:
    genai = None
try:
    from google.api_core import exceptions as gex
except Exception:
    gex = None

# Nếu bạn muốn gọi Gemini thật:
# from google.generativeai import GenerativeModel
# model = GenerativeModel("gemini-pro")


# ================================================
# HÀM XÂY DỰNG PROMPT CHO LLM
# ================================================
def build_prompt(facts, rule_conclusions, bayes_output, fired_rules, final_class):
    compressed_facts = "; ".join([
        f"job={facts.get('job')}",
        f"income_monthly={facts.get('income_monthly')}",
        f"expense_monthly={facts.get('expense_monthly')}",
        f"debt_amount={facts.get('debt_amount')}",
        f"income_expense_ratio={facts.get('income_expense_ratio')}",
        f"debt_ratio={facts.get('debt_ratio')}",
        f"late_payments_12m={facts.get('late_payments_12m')}",
        f"credit_history_length_years={facts.get('credit_history_length_years')}",
        f"new_credit_accounts={facts.get('new_credit_accounts')}",
        f"credit_mix={facts.get('credit_mix')}"
    ])

    prompt = f"""
Hãy viết báo cáo theo đúng 7 đoạn, mỗi đoạn 3–4 câu: 

1) Mô tả nghề nghiệp, thu nhập, chi tiêu và ý nghĩa income_expense_ratio. 
2) Phân tích khoản nợ (debt_amount, debt_ratio) và mức rủi ro. 
3) Đánh giá hành vi tín dụng: trả chậm 12 tháng, số năm lịch sử tín dụng, số tài khoản mới. 
4) Phân tích chất lượng credit_mix và yếu tố cải thiện/suy giảm hồ sơ. 
5) Tổng hợp các yếu tố ảnh hưởng đến năng lực tín dụng và mức an toàn tài chính. 
6) Đưa ra quyết định xếp loại tín dụng (good / fair / bad) và lý do chính. 
7) Đề xuất các hướng cải thiện hành vi tài chính hoặc điểm tín dụng. 

Yêu cầu văn phong rõ ràng, chuyên nghiệp, lập luận tài chính mạch lạc. 
Không viết tắt, không lặp lại thông tin không cần thiết. 

Dữ liệu đầu vào: {compressed_facts}
"""

    return prompt


# ================================================
# HÀM GỌI GEMINI (CÓ THỂ OFFLINE NẾU KO CÓ KEY)
# ================================================
def call_gemini(prompt: str):
    key = os.environ.get("GOOGLE_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")
    if not genai:
        raise RuntimeError("google-generativeai not installed")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY missing")
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name)
    try:
        result = model.generate_content(prompt)
    except Exception as e:
        if gex and isinstance(e, gex.ResourceExhausted):
            raise RuntimeError("Gemini rate-limit exceeded")
        raise RuntimeError(str(e))
    text = getattr(result, "text", "")
    if not text:
        raise RuntimeError("No output from Gemini")
    return text


# ================================================
# HÀM SINH GIẢI THÍCH (HÀM DÙNG TRONG CONTROLLER)
# ================================================
def generate_explanation(facts, rule_conclusions, bayes_output, fired_rules, final_class):
    prompt = build_prompt(
        facts=facts,
        rule_conclusions=rule_conclusions,
        bayes_output=bayes_output,
        fired_rules=fired_rules,
        final_class=final_class,
    )
    return call_gemini(prompt)


# ================================================
# TEST THỬ
# ================================================
if __name__ == "__main__":
    sample_facts = {
        "income_expense_ratio": 1.4,
        "debt_ratio": 0.25,
        "late_payments_12m": 2,
        "credit_history_length_years": 6,
        "new_credit_accounts": 1,
        "credit_mix": "fair"
    }

    sample_rule = {
        "financial_capacity": "stable",
        "debt_risk": "medium",
        "payment_behavior": "average",
        "credit_history_quality": "medium",
        "overall_risk": "medium",
        "rule_credit_class": "fair"
    }

    sample_bayes = {
        "bayes_class": "fair",
        "confidence": 0.65,
        "bayes_score": 670
    }

    sample_fired = ["R2_income_stable", "R5_debt_medium", "R8_few_late", "R11_history_medium", "R20_mediumrisk_combination"]

    result = generate_explanation(
        facts=sample_facts,
        rule_conclusions=sample_rule,
        bayes_output=sample_bayes,
        fired_rules=sample_fired,
        final_class="fair"
    )

    print(result)
