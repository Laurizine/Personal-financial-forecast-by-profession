## Chuẩn Bị Môi Trường
- Yêu cầu: Python 3.10+ trên Windows.
- Mở terminal tại thư mục dự án: `e:\CS 2022\Knowledge representation and reasoning\Final`.
- Cài đặt phụ thuộc: `python -m pip install -r requirements.txt`.

## Huấn Luyện/Khởi Tạo Mô Hình Bayesian
- File mô hình sẽ lưu tại: `inference/model.pkl` (đặt trong `config/settings.py`).
- Dataset mặc định: `Dataset/simulated_data.csv`.
- Huấn luyện nhanh bằng CLI có sẵn: `python run.py train`.
- Nếu `model.pkl` đã tồn tại, có thể bỏ qua bước huấn luyện.

## Thiết Lập API Key Gemini (tuỳ chọn)
- Để LLM dùng Google Gemini, đặt biến môi trường:
  - PowerShell: `setx GOOGLE_API_KEY "<YOUR_API_KEY>"`
- Đóng và mở lại terminal sau khi `setx` để biến môi trường có hiệu lực.
- Nếu không có key, phần LLM sẽ dùng mô tả fallback sinh từ `facts`.

## Chạy UI Streamlit
- Lệnh: `streamlit run app/ui_streamlit.py`.
- Nhập các trường: `job`, `income_monthly`, `expense_monthly`, `debt_amount`, `late_payments_12m`, `credit_history_length_years`, `new_credit_accounts`, `credit_mix`.
- Kết quả hiển thị gồm: lớp tín dụng Bayesian, kết luận rule engine, các rule đã kích hoạt, và “Giải thích (LLM)” sinh từ Gemini hoặc fallback.

## Chạy API FastAPI (tuỳ chọn)
- Lệnh: `uvicorn app.api:app --reload` (mặc định cổng `http://127.0.0.1:8000`).
- Gọi thử endpoint `/explain`:
  - `curl -X POST http://127.0.0.1:8000/explain -H "Content-Type: application/json" -d "{ \"job\": \"Teacher\", \"income_monthly\": 15000000, \"expense_monthly\": 10000000, \"debt_amount\": 5000000, \"late_payments_12m\": 1, \"credit_history_length_years\": 4, \"new_credit_accounts\": 0, \"credit_mix\": \"good\" }"`
- Phản hồi JSON gồm: `final_class`, `bayesian`, `rule_conclusions`, `fired_rules`, `facts`, `explanation`.

## CLI Dự Báo Nhanh (không UI)
- Dùng `run.py predict` với JSON inline:
  - `python run.py predict --input "{\"job\":\"Nurse\",\"income_monthly\":20000000,\"expense_monthly\":15000000,\"debt_amount\":0,\"late_payments_12m\":4,\"credit_history_length_years\":4,\"new_credit_accounts\":3,\"credit_mix\":\"good\"}"`
- In ra JSON gồm kết quả rule và dự báo Bayesian.

## Lưu Ý / Khắc Phục Sự Cố
- Thiếu thư viện: chạy lại `python -m pip install -r requirements.txt`.
- Chưa có `model.pkl`: chạy `python run.py train` để huấn luyện.
- `GOOGLE_API_KEY` chưa nhận: đảm bảo đặt bằng `setx` và mở lại terminal.
- UI Streamlit báo lỗi form trùng key: đã được sửa trong `app/ui_streamlit.py`; dùng UI hiện tại.
