# Hệ thống chuyên gia dự đoán điểm tín dụng (Rules + Bayesian + Gemini)

Dự án kết hợp tập luật (forward-chaining), mô hình Bayesian (Gaussian Naive Bayes + preprocessing) và LLM (Google Gemini) để phân tích hồ sơ tín dụng, đưa ra phân loại và giải thích chi tiết bằng tiếng Việt.

## Công nghệ & phương pháp
- UI: `streamlit`
- API: `fastapi` + `uvicorn`
- ML: `scikit-learn` với `StandardScaler`, `OneHotEncoder`, `GaussianNB`, `Pipeline`
- LLM: `google-generativeai` với model `gemini-2.5-flash` (chỉ dùng model này khi gọi API)
- Suy luận: Rule Engine forward-chaining (`knowledge/rule_engine.py`)
- Prompt LLM: 7 đoạn tiếng Việt, nén facts dạng `key=value` để giảm token

## Cấu trúc dự án
- `app/controller.py`: gom lý luận, gọi Rule Engine + Bayesian + LLM
- `app/ui_streamlit.py`: UI người dùng (có cache theo input và throttle 5s)
- `app/api.py`: REST API `/explain`
- `knowledge/rules.py`, `knowledge/rule_engine.py`: tập luật và máy suy diễn forward-chaining
- `inference/bayesian_model.py`: pipeline huấn luyện/dự đoán (GaussianNB), lưu tại `inference/model.pkl`
- `llm/explanation_service.py`: xây dựng prompt và gọi Gemini (không dùng fallback)
- `config/settings.py`: đường dẫn dataset/model
- `env/set_gemini.ps1`: script thiết lập API key và model
- `Dataset/simulated_data.csv`: dữ liệu mẫu
- `tests/`: kiểm thử đơn vị

## Yêu cầu hệ thống
- Python 3.10 trở lên (Windows)
- `pip` đã cài đặt

## Cài đặt phụ thuộc
`python -m pip install -r requirements.txt`

## Các bước chạy
1) Cho phép chạy script PowerShell (Windows)
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

2) Thiết lập API key và chọn model (CHỈ dùng `gemini-2.5-flash`)
- `.\env\set_gemini.ps1 -API_KEY "API_KEY_CUA_BAN" -MODEL "gemini-2.5-flash"`
  - Có thể đổi tên model tại tham số `-MODEL` (khuyến nghị `gemini-2.5-flash`).

3) (Tuỳ chọn) Huấn luyện mô hình Bayesian
- `python run.py train`
  - Dataset mặc định: `Dataset/simulated_data.csv`
  - Model lưu tại: `inference/model.pkl`

4) Chạy UI Streamlit
- `streamlit run app/ui_streamlit.py`
  - Nhập các trường: `job`, `income_monthly`, `expense_monthly`, `debt_amount`, `late_payments_12m`, `credit_history_length_years`, `new_credit_accounts`, `credit_mix`
  - UI hiển thị: kết luận cuối (`final_class`), dự đoán Bayesian (`bayesian`), kết luận luật (`rule_conclusions`), các luật kích hoạt (`fired_rules`), giải thích LLM (`llm_explanation`)

5) (Tuỳ chọn) Chạy REST API
- `uvicorn app.api:app --reload`
- Ví dụ gọi:
  - `curl -X POST http://127.0.0.1:8000/explain -H "Content-Type: application/json" -d "{...}"`

6) (Tuỳ chọn) CLI nhanh
- `python run.py predict --input "{...}"`

## Lựa chọn mode khi bị limit (429)
- Chế độ tiêu chuẩn: dùng Gemini với cache theo input và throttle 5s; khi 429, UI hiển thị lỗi ngắn gọn, chờ rồi thử lại
- Chế độ hạn chế: tăng `LLM_MIN_INTERVAL_SEC` (ví dụ 10–15s) để giảm tần suất gọi
- Chế độ không LLM (tạm thời): chạy chỉ Rules + Bayesian (không cấu hình `GOOGLE_API_KEY`)

## Cấu hình LLM
- Biến môi trường: `GOOGLE_API_KEY`, `GEMINI_MODEL` (mặc định `gemini-2.5-flash`), tuỳ chọn `LLM_MIN_INTERVAL_SEC`
- Lưu ý: Không commit API key, không đưa vào mã nguồn

## Khắc phục sự cố
- Thiếu thư viện: `python -m pip install -r requirements.txt`
- Chưa có `inference/model.pkl`: `python run.py train`
- `GOOGLE_API_KEY` chưa nhận: chạy script `env/set_gemini.ps1` hoặc mở lại terminal
- Cổng API bị chiếm dụng: `uvicorn app.api:app --reload --port 8001`
- Lỗi 429 rate-limit: đợi 30–60 giây rồi thử lại; tránh bấm liên tục

## Kiểm thử
- `python -m unittest discover -s tests`
