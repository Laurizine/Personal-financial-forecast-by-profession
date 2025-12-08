## Đầu ra mong muốn
- Cung cấp API REST để nhận payload tài chính, chạy rules + model, trả về kết quả dự đoán kèm phần mô tả rõ ràng (explanation).

## Cách làm
- Thêm `app/api.py` dùng FastAPI:
  - `POST /explain` → nhận JSON payload, gọi `CreditController().process(payload)`, trả `final_class`, `bayesian`, `rule_conclusions`, `fired_rules`, `facts`, `explanation`.
- Bổ sung dependencies vào `requirements.txt`: `fastapi`, `uvicorn`.

## Chạy
- `conda activate krr`
- `python -m pip install -r requirements.txt`
- `uvicorn app.api:app --host 0.0.0.0 --port 8000`

## Test
- Gọi `POST http://localhost:8000/explain` với JSON mẫu từ dataset; nhận lại kết quả đầy đủ cùng mô tả.

Cho phép tôi triển khai các thay đổi này ngay.