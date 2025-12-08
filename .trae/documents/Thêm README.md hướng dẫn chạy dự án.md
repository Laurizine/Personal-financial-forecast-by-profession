## Mục tiêu
- Tạo file README.md ở thư mục gốc, viết hướng dẫn đầy đủ để chạy dự án bằng Streamlit, FastAPI, CLI và cấu hình Gemini.

## Nội dung README
- Giới thiệu ngắn: Hệ thống chuyên gia tín dụng (Rules + Bayesian + LLM Gemini).
- Yêu cầu: Python 3.10+, pip.
- Cài đặt: `python -m pip install -r requirements.txt`.
- Huấn luyện mô hình: `python run.py train` (dataset `Dataset/simulated_data.csv`, model lưu `inference/model.pkl`).
- Chạy UI Streamlit: `streamlit run app/ui_streamlit.py`.
- Chạy API FastAPI: `uvicorn app.api:app --reload` và ví dụ gọi `/explain`.
- CLI predict: `python run.py predict --input "{...}"`.
- Thiết lập Gemini: `setx GOOGLE_API_KEY "<YOUR_API_KEY>"` (Windows), lưu ý không đưa key vào mã nguồn.
- Khắc phục sự cố: thiếu thư viện, chưa có `model.pkl`, biến môi trường chưa nhận, cổng bị chiếm dụng.

## Phạm vi thay đổi
- Chỉ thêm file `README.md` ở thư mục gốc; không chỉnh sửa code thực thi.

## Kiểm tra
- Xác minh câu lệnh hoạt động trên Windows.
- Đảm bảo nội dung bằng tiếng Việt, rõ ràng, dễ làm theo.