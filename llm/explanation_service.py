import json
import textwrap
import os
try:
    import google.generativeai as genai
except Exception:
    genai = None

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
    key = os.environ.get("GOOGLE_API_KEY", "")
    if genai and key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-pro")
            result = model.generate_content(prompt)
            return getattr(result, "text", "") or ""
        except Exception:
            return ""
    return ""


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

    explanation = call_gemini(prompt)
    if explanation:
        return explanation

    job = facts.get("job")
    income = facts.get("income_monthly", 0)
    expense = facts.get("expense_monthly", 0)
    ier = facts.get("income_expense_ratio", 0)
    debt = facts.get("debt_amount", 0)
    dr = facts.get("debt_ratio", 0)
    late = facts.get("late_payments_12m", 0)
    hist = facts.get("credit_history_length_years", 0)
    new_acc = facts.get("new_credit_accounts", 0)
    mix = facts.get("credit_mix", "")

    ier_desc = "rất tốt" if ier >= 1.6 else ("ổn định" if ier >= 1.5 else ("hạn chế" if ier >= 1.2 else "dưới mức an toàn"))
    dr_desc = "rất tốt" if dr == 0 else ("thấp" if dr < 0.2 else ("trung bình" if dr < 0.5 else "cao"))
    late_desc = "khá tiêu cực" if late >= 3 else ("cần cải thiện" if late >= 1 else "tốt")
    hist_desc = "yếu" if hist < 5 else ("trung bình" if hist < 10 else "tốt")
    new_acc_risk = "tăng rủi ro do mở nhiều tài khoản mới" if new_acc >= 3 else ("chấp nhận được" if new_acc <= 1 else "cần theo dõi")

    p1 = (
        f"1) Người dùng là một {job}; thu nhập hàng tháng {income:,.0f} VND, chi tiêu {expense:,.0f} VND. "
        f"Chỉ số income_expense_ratio = {ier:.2f}, mức {ier_desc}, phản ánh khả năng tài chính {'vững' if ier_desc in ['rất tốt','ổn định'] else 'cần cải thiện'}."
    )

    p2 = (
        f"2) Khoản nợ hiện tại: {'không có' if debt==0 else f'{debt:,.0f} VND'}. Tỷ lệ nợ (debt_ratio = {dr:.2f}) ở mức {dr_desc}, "
        f"đánh giá tổng quan là {'tích cực' if dr_desc in ['rất tốt','thấp'] else ('trung tính' if dr_desc=='trung bình' else 'tiêu cực')}."
    )

    p3 = (
        f"3) Hành vi tín dụng: {late} lần trả chậm/12 tháng ({late_desc}); lịch sử tín dụng {hist} năm ({hist_desc}); "
        f"số tài khoản tín dụng mới {new_acc} ({new_acc_risk}). Các yếu tố này ảnh hưởng trực tiếp tới rủi ro hành vi."
    )

    p4 = (
        f"4) Credit_mix: \"{mix}\". Mức độ đa dạng hoá danh mục tín dụng {'tốt' if mix=='good' else ('cân bằng' if mix=='fair' else 'hạn chế')}. "
        f"Yếu tố cải thiện: đa dạng hoá hợp lý và duy trì kỷ luật trả nợ; yếu tố suy giảm: mở tài khoản dồn dập và trả chậm."
    )

    positives = []
    negatives = []
    if ier >= 1.3:
        positives.append("tỷ lệ thu/chi lành mạnh")
    else:
        negatives.append("tỷ lệ thu/chi thấp")
    if dr == 0 or dr < 0.2:
        positives.append("nghĩa vụ nợ thấp")
    elif dr >= 0.5:
        negatives.append("tỷ lệ nợ cao")
    if late >= 3:
        negatives.append("nhiều lần trả chậm")
    elif late == 0:
        positives.append("không có trả chậm")
    if hist >= 10:
        positives.append("lịch sử tín dụng dài")
    elif hist < 5:
        negatives.append("lịch sử tín dụng ngắn")
    if new_acc >= 3:
        negatives.append("mở nhiều tài khoản mới")
    elif new_acc == 0:
        positives.append("không mở thêm tài khoản mới")

    p5 = (
        f"5) Tổng hợp: yếu tố tích cực gồm {', '.join(positives) if positives else 'ít yếu tố nổi bật'}; "
        f"yếu tố tiêu cực gồm {', '.join(negatives) if negatives else 'hạn chế không đáng kể'}. "
        f"Đánh giá mức độ an toàn tài chính hiện tại là {'khá tốt' if len(negatives)==0 else ('trung bình' if len(negatives)<=2 else 'cần thận trọng')}."
    )

    p6 = (
        f"6) Quyết định xếp loại tín dụng cuối cùng: {str(final_class).lower()}."
    )

    suggestions = []
    if ier < 1.3:
        suggestions.append("tăng thu nhập hoặc tối ưu chi tiêu để nâng income_expense_ratio")
    if dr >= 0.2:
        suggestions.append("giảm dư nợ, ưu tiên trả các khoản lãi cao")
    if late >= 1:
        suggestions.append("thiết lập nhắc hạn thanh toán, tự động hoá trả nợ")
    if hist < 5:
        suggestions.append("duy trì tài khoản hiện tại ổn định để kéo dài lịch sử tín dụng")
    if new_acc >= 3:
        suggestions.append("hạn chế mở thêm tài khoản mới trong ngắn hạn")

    p7 = (
        f"7) Gợi ý cải thiện: {('; '.join(suggestions)) if suggestions else 'duy trì kỷ luật tài chính hiện tại'}."
    )

    return "\n\n".join([p1, p2, p3, p4, p5, p6, p7])


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
