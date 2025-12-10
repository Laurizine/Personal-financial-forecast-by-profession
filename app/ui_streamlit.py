import os, sys, time, json
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import streamlit as st
from app.controller import CreditController

# Khởi tạo controller
controller = CreditController()

# =============================
#  GIAO DIỆN CHÍNH
# =============================
st.set_page_config(page_title="Credit Scoring Expert System", layout="centered")

st.title("🔍 Hệ thống chuyên gia dự đoán điểm tín dụng")
st.write("Nhập thông tin tài chính để hệ thống suy luận theo tập luật + mô hình Bayesian.")

st.divider()

# =============================
# FORM NHẬP LIỆU
# =============================
st.header("📌 Nhập thông tin của bạn")

with st.form("credit_form"):
    col1, col2 = st.columns(2)

    with col1:
        job = st.selectbox(
            "Nghề nghiệp:",
            [
                "IT Engineer", "Data Analyst", "Teacher", "Nurse", "Accountant",
                "Salesperson", "Freelancer", "Designer", "Mechanic", "Student"
            ],
        )
        income = st.number_input("Thu nhập hàng tháng (VND):", min_value=0)
        expense = st.number_input("Chi tiêu hàng tháng (VND):", min_value=0)
        debt = st.number_input("Tổng nợ hiện tại (VND):", min_value=0)

    with col2:
        late = st.number_input("Số lần trả chậm (12 tháng):", min_value=0, max_value=20)
        history = st.number_input("Số năm lịch sử tín dụng:", min_value=0, max_value=40)
        new_acc = st.number_input("Số tài khoản tín dụng mới:", min_value=0, max_value=10)
        mix = st.selectbox("Credit Mix:", ["good", "fair", "poor"])

    submitted = st.form_submit_button("🔮 Dự báo điểm tín dụng")

# =============================
# XỬ LÝ KHI SUBMIT FORM
# =============================
if submitted:
    st.subheader("📊 Kết quả phân tích")

    user_input = {
        "job": job,
        "income_monthly": income,
        "expense_monthly": expense,
        "debt_amount": debt,
        "late_payments_12m": late,
        "credit_history_length_years": history,
        "new_credit_accounts": new_acc,
        "credit_mix": mix,
    }

    # Gọi controller
    result = controller.process(user_input)

    # =============================
    # HIỂN THỊ KẾT QUẢ
    # =============================
    st.markdown("### 🎯 **Kết luận cuối cùng:**")
    st.markdown(
        f"<h2 style='color:#0099ff'> {result['final_class'].upper()} </h2>",
        unsafe_allow_html=True
    )

    # Bayesian
    st.subheader("📈 Dự đoán từ Bayesian Model:")
    st.write(f"• Lớp tín dụng dự đoán: **{result['bayesian']['bayes_class']}**")
    st.write(f"• Điểm tín dụng ước tính: **{result['bayesian']['bayes_score']}**")
    st.write(f"• Độ tự tin mô hình: **{round(result['bayesian']['confidence'] * 100, 2)}%**")

    # Rule conclusions
    st.subheader("🧠 Kết luận từ tập luật (Rule Engine):")
    st.json(result["rule_conclusions"])

    st.subheader("📜 Các luật được kích hoạt:")
    st.write(result["fired_rules"])

    # Explanation
    st.subheader("💬 Giải thích (LLM):")
    st.write(result["llm_explanation"])

    # Raw facts processing
    with st.expander("📂 Dữ liệu đã xử lý (Facts):"):
        st.json(result["facts"])
 
