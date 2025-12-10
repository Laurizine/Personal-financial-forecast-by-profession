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
    facts_json = json.dumps(facts, indent=2, ensure_ascii=False)

    prompt = f"""
Bạn là chuyên gia phân tích tín dụng. Hãy mô tả và đánh giá hồ sơ tín dụng của người dùng dựa trên dữ liệu sau:

{facts_json}

Yêu cầu trình bày kết quả theo đúng 7 đoạn sau:

1) Mô tả nghề nghiệp, thu nhập, chi tiêu và giải thích ý nghĩa của chỉ số income_expense_ratio đối với khả năng tài chính.

2) Phân tích khoản nợ hiện tại, tính chất của debt_amount và đánh giá mức độ rủi ro dựa trên debt_ratio (tích cực hay tiêu cực).

3) Đánh giá hành vi tín dụng gồm: số lần trả chậm trong 12 tháng, số năm lịch sử tín dụng và số tài khoản tín dụng mới. Giải thích rủi ro tương ứng.

4) Phân tích chất lượng credit_mix và nêu rõ các yếu tố nào đang cải thiện hoặc làm suy giảm chất lượng hồ sơ tín dụng.

5) Tổng hợp toàn bộ các yếu tố quan trọng ảnh hưởng đến năng lực tín dụng và đánh giá mức độ an toàn tài chính hiện tại.

6) Đưa ra quyết định xếp loại tín dụng cuối cùng (good / fair / bad) dựa trên nội dung phân tích.

7) Đề xuất các gợi ý cải thiện điểm tín dụng hoặc hành vi tài chính phù hợp với tình trạng hiện tại.

Yêu cầu văn phong:
- Rõ ràng, chuyên nghiệp, có tính giải thích.
- Thể hiện lập luận tài chính mạch lạc.
- Trình bày đầy đủ, không viết tắt, không bỏ sót thông tin.
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
