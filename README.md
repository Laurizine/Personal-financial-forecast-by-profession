# Hệ thống chuyên gia dự đoán điểm tín dụng (Rules + Bayesian + LLM)

Dự án kết hợp tập luật (forward-chaining), mô hình Bayesian và LLM (Google Gemini) để phân tích hồ sơ tín dụng, đưa ra phân loại và giải thích chi tiết bằng tiếng Việt.

## Yêu cầu hệ thống
- Python 3.10 trở lên (Windows)
- pip đã cài đặt

## Cài đặt phụ thuộc
```bash
python -m pip install -r requirements.txt
```

## Huấn luyện mô hình Bayesian
- Dataset mặc định: `Dataset/simulated_data.csv`
- Mô hình sẽ lưu tại: `inference/model.pkl` (cấu hình trong `config/settings.py`)
- Lệnh huấn luyện:
```bash
python run.py train
```
- Nếu `model.pkl` đã tồn tại, có thể bỏ qua bước này.

## Chạy giao diện Streamlit (UI)
```bash
streamlit run app/ui_streamlit.py
```
- Nhập các trường: `job`, `income_monthly`, `expense_monthly`, `debt_amount`, `late_payments_12m`, `credit_history_length_years`, `new_credit_accounts`, `credit_mix`.
- UI hiển thị:
  - Kết luận cuối cùng (`final_class`)
  - Dự đoán từ Bayesian (`bayesian`: lớp/điểm/độ tự tin)
  - Kết luận từ rule engine (`rule_conclusions`) và các luật kích hoạt (`fired_rules`)
  - Giải thích (LLM) từ Gemini hoặc fallback (dựa trên `facts`)

## Chạy REST API với FastAPI (tuỳ chọn)
```bash
uvicorn app.api:app --reload
```
- Endpoint: `POST /explain`
- Gọi thử (ví dụ dùng curl):
```bash
curl -X POST http://127.0.0.1:8000/explain \
  -H "Content-Type: application/json" \
  -d "{ \"job\": \"Teacher\", \"income_monthly\": 15000000, \"expense_monthly\": 10000000, \"debt_amount\": 5000000, \"late_payments_12m\": 1, \"credit_history_length_years\": 4, \"new_credit_accounts\": 0, \"credit_mix\": \"good\" }"
```
- Phản hồi JSON gồm: `final_class`, `bayesian`, `rule_conclusions`, `fired_rules`, `facts`, `explanation`.

## Dự báo nhanh bằng CLI (không UI)
```bash
python run.py predict --input "{\"job\":\"Nurse\",\"income_monthly\":20000000,\"expense_monthly\":15000000,\"debt_amount\":0,\"late_payments_12m\":4,\"credit_history_length_years\":4,\"new_credit_accounts\":3,\"credit_mix\":\"good\"}"
```
- In ra JSON gồm kết quả rule-engine và dự báo Bayesian.

## Thiết lập Google Gemini (LLM)
- Đặt biến môi trường API key (Windows):
```powershell
setx GOOGLE_API_KEY "<YOUR_API_KEY>"
```
- Đóng và mở lại terminal để biến môi trường có hiệu lực.
- Lưu ý: Không đưa API key trực tiếp vào mã nguồn hoặc commit.

## Khắc phục sự cố
- Thiếu thư viện: chạy lại `python -m pip install -r requirements.txt`.
- Chưa có `inference/model.pkl`: chạy `python run.py train`.
- `GOOGLE_API_KEY` chưa nhận: đảm bảo `setx` và mở lại terminal.
- Cổng API bị chiếm dụng: chạy `uvicorn app.api:app --reload --port 8001`.
- Lỗi form Streamlit trùng key: UI đã dùng một form duy nhất `credit_form` trong `app/ui_streamlit.py`.

## Cấu trúc liên quan
- `app/controller.py`: gom lý luận, gọi rule engine + Bayesian + LLM.
- `knowledge/rules.py`, `knowledge/rule_engine.py`: tập luật và suy diễn.
- `inference/bayesian_model.py`: pipeline huấn luyện/dự đoán Bayesian.
- `llm/explanation_service.py`: xây dựng prompt và gọi Gemini, fallback 7 đoạn.
- `app/ui_streamlit.py`: giao diện người dùng.
- `app/api.py`: REST API `/explain`.
