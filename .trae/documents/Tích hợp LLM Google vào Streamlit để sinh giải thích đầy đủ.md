## Mục tiêu
- Dùng Streamlit như hiện tại, tích hợp API LLM của Google (Gemini) để sinh giải thích đầy đủ từ dữ liệu đã xử lý.

## Thay đổi cần thực hiện
- Cập nhật `llm/explanation_service.py`: nếu có `GOOGLE_API_KEY` trong biến môi trường thì gọi Gemini thật, nếu không thì fallback offline.
- Bổ sung `google-generativeai` vào `requirements.txt` để cài đặt phụ thuộc.
- UI Streamlit giữ nguyên: phần giải thích sẽ dùng kết quả từ controller (tự động gọi LLM nếu có API key).

## Cách chạy
- `conda activate krr`
- `python -m pip install -r requirements.txt`
- Đặt khóa: `set GOOGLE_API_KEY=YOUR_KEY`
- `python -m streamlit run app/ui_streamlit.py`
- Nhập form hoặc gửi JSON đã xử lý; phần “Giải thích (LLM)” sẽ hiển thị câu trả lời chi tiết.

Cho phép tôi triển khai các thay đổi này ngay.