# Hệ thống chuyên gia dự đoán điểm tín dụng (Rules + Bayesian + Gemini)

Dự án kết hợp tập luật (forward-chaining), mô hình Bayesian (Gaussian Naive Bayes + preprocessing) và LLM (Google Gemini) để phân tích hồ sơ tín dụng, đưa ra phân loại và giải thích chi tiết bằng tiếng Việt.

## Công nghệ & phương pháp
- UI: `streamlit`
- API: `fastapi` (không dùng uvicorn theo yêu cầu)
- ML: `scikit-learn` với `StandardScaler`, `OneHotEncoder`, `GaussianNB`, `Pipeline`
- LLM: `google-generativeai` với model `gemini-2.5-flash` (chỉ dùng model này khi gọi API)
- Suy luận: Rule Engine forward-chaining (`knowledge/rule_engine.py`)
- Prompt LLM: 7 đoạn tiếng Việt, nén facts dạng `key=value` để giảm token

## Cấu trúc dự án
- `app/`
  - `ui_streamlit.py`: Giao diện người dùng, cache theo input và throttle 5s
  - `controller.py`: Trung tâm xử lý, chuẩn hóa facts, gọi Rules + Bayesian + LLM
  - `api.py`: Định nghĩa FastAPI cho tích hợp nội bộ (không chạy uvicorn)
- `knowledge/`
  - `rules.py`: Tập luật nghiệp vụ (if-then), gồm các nhóm năng lực tài chính, rủi ro nợ, hành vi thanh toán, chất lượng lịch sử, tín dụng mới, mix tín dụng, tổng hợp rủi ro và gợi ý lớp tín dụng
  - `rule_engine.py`: Máy suy diễn tiến, áp dụng luật lặp cho đến khi ổn định
- `inference/`
  - `bayesian_model.py`: Pipeline GaussianNB (preprocess + model), train/predict, lưu `model.pkl`
  - `model.pkl`: Mô hình đã huấn luyện
- `llm/`
  - `explanation_service.py`: Tạo prompt 7 đoạn, nén facts, gọi Gemini; chỉ Gemini, không fallback
- `config/`
  - `settings.py`: Đường dẫn dataset/model và cấu hình chung
- `Dataset/`
  - `simulated_data.csv`: Dữ liệu mẫu để train
- `env/`
  - `set_gemini.ps1`: Thiết lập `GOOGLE_API_KEY`, `GEMINI_MODEL` (mặc định `gemini-2.5-flash`)
- `tests/`
  - `test_end_to_end.py`: Kiểm thử luồng end-to-end qua `CreditController`
  - `test_edge_cases.py`: Biên/ngoại lệ (0, cực lớn, thiếu trường)
  - `test_rule_coverage.py`: Phủ nhánh rule, tránh ghi đè sai giữa R19/R20
  - `test_bayesian.py`, `test_bayesian_stability.py`: Kiểm thử huấn luyện/dự đoán và độ ổn định
  - `test_fact_normalization.py`: Kiểm thử chuẩn hóa facts
  - `test_llm_fallback.py`: Kiểm thử khi Gemini lỗi (mock) trả về thông báo ngắn gọn
- `visualization/`: Công cụ vẽ biểu đồ đánh giá/nhân quả
- File gốc: `run.py`, `requirements.txt`, `README.md`

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

5) (Tuỳ chọn) REST API
- Dự án có định nghĩa FastAPI trong `app/api.py` để tích hợp nội bộ.
- Không dùng uvicorn theo yêu cầu; ưu tiên Streamlit.

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
- Cài đặt pytest: `pip install pytest`
- Chạy toàn bộ: `python -m pytest tests`
- Phạm vi bao phủ:
  - End-to-end controller, biên/ngoại lệ, phủ nhánh rule (đã xử lý xung đột R19/R20), ổn định Bayesian, chuẩn hóa facts, và fallback LLM khi lỗi.
