import os, sys, time, json
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import streamlit as st
from app.controller import CreditController

# Khởi tạo controller
@st.cache_resource
def get_controller():
    return CreditController()

controller = get_controller()

@st.cache_data(ttl=1800, max_entries=512)
def compute_result(payload):
    return controller.process(payload)

# =============================
#  GIAO DIỆN CHÍNH
# =============================
st.set_page_config(page_title="Merry Christmas Credit Analyzer", page_icon="🎄", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"]  {
      font-family: 'Poppins', sans-serif;
      background-image: url('https://images.unsplash.com/photo-1601047668511-77486e0f9b06?auto=format&fit=crop&w=2067&q=80');
      background-size: cover;
      background-attachment: fixed;
      background-position: center;
    }
    .xmas-title {
      font-family: 'Mountains of Christmas', cursive;
      font-size: 64px;
      color: #FFFFFF;
      text-align: center;
      text-shadow: 0 0 4px #FFD54F, 0 0 10px #FFD54F, 2px 2px 0 #D32F2F;
      margin-top: 10px;
    }
    .xmas-subtitle {
      font-family: 'Poppins', sans-serif;
      font-size: 18px;
      color: #FFFFFF;
      text-align: center;
      margin-bottom: 20px;
    }
    .gold-border {
      border: 2px solid #FFD54F;
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
      background: rgba(255,255,255,0.85);
      padding: 24px;
    }
    .card {
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
      background: rgba(255,255,255,0.9);
      padding: 24px;
      backdrop-filter: blur(3px);
    }
    .stButton > button {
      background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
      color: #fff;
      border: 2px solid #FFD54F;
      border-radius: 14px;
      padding: 10px 20px;
      font-weight: 600;
      box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }
    .stButton > button:hover {
      background: linear-gradient(135deg, #C62828 0%, #8E0000 100%);
      transform: translateY(-1px);
    }
    .snow {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      pointer-events: none;
      background-image: radial-gradient(white 1px, transparent 1px);
      background-size: 3px 3px;
      animation: snowfall 15s linear infinite;
      opacity: 0.6;
    }
    @keyframes snowfall {
      0% { background-position: 0 0; }
      100% { background-position: 0 1000px; }
    }
    </style>
    <div class="snow"></div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='xmas-title'>🎄 Merry Christmas Credit Analyzer 🎁</div>", unsafe_allow_html=True)
st.markdown("<div class='xmas-subtitle'>✨ Phân tích tín dụng với Rules + Bayesian + Gemini ✨</div>", unsafe_allow_html=True)

# =============================
# FORM NHẬP LIỆU
# =============================
st.markdown("<div class='gold-border card'><h3 style='margin-top:0'>📌 Nhập thông tin của bạn</h3>", unsafe_allow_html=True)

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

    submitted = st.form_submit_button("🎅 Dự báo điểm tín dụng")

# =============================
# XỬ LÝ KHI SUBMIT FORM
# =============================
if submitted:
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='gold-border card'><h3 style='margin-top:0'>📊 Kết quả phân tích</h3>", unsafe_allow_html=True)

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

    # --- Cache & Throttle ---
    payload_key = json.dumps(user_input, sort_keys=True, ensure_ascii=False)
    min_interval = float(os.environ.get("LLM_MIN_INTERVAL_SEC", "5"))

    last_key = st.session_state.get("last_key")
    last_result = st.session_state.get("last_result")
    last_call = st.session_state.get("last_call_at")
    now = time.time()

    if last_key == payload_key and last_result is not None:
        result = last_result
    else:
        if last_call and (now - last_call < min_interval):
            wait_time = min_interval - (now - last_call)
            st.warning(f"Vui lòng đợi {round(wait_time, 1)} giây trước khi gọi lại.")
            if last_result is not None:
                result = last_result
            else:
                st.stop()
        else:
            result = compute_result(user_input)
            st.session_state["last_key"] = payload_key
            st.session_state["last_result"] = result
            st.session_state["last_call_at"] = now

    # =============================
    # HIỂN THỊ KẾT QUẢ
    # =============================
    st.markdown("<h4>🎯 Kết luận cuối cùng:</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:36px;color:#1B5E20;font-weight:700;text-shadow:0 0 6px #FFD54F, 2px 2px 0 #D32F2F'>{result['final_class'].upper()}</div>", unsafe_allow_html=True)

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
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#fff;margin-top:24px'>Made with ❤️ during Christmas Season</p>", unsafe_allow_html=True)