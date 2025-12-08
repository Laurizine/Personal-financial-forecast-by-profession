## Mục tiêu
- Chỉnh hàm `generate_explanation(...)` để khi Gemini không trả về kết quả, phần fallback sẽ sinh lời giải thích theo đúng 7 đoạn như prompt đã cập nhật, dựa trên `facts`.

## Thay đổi kỹ thuật
- Giữ nguyên `build_prompt(...)` (đã dùng mẫu 7 đoạn chỉ dựa trên facts).
- Cập nhật phần fallback trong `generate_explanation(...)`:
  - Tạo 7 đoạn: (1) nghề nghiệp/thu nhập/chi tiêu/IER, (2) nợ và debt_ratio, (3) hành vi tín dụng (trả chậm, lịch sử, tài khoản mới), (4) credit_mix và yếu tố cải thiện/suy giảm, (5) tổng hợp các yếu tố quan trọng, (6) quyết định xếp loại (dùng `final_class`), (7) gợi ý cải thiện có điều kiện theo `facts`.

## Kiểm tra
- Chạy thử với bộ `facts` mẫu (Nurse...) để xác nhận văn bản có đủ 7 đoạn, tiếng Việt, mạch lạc.

## Phạm vi
- Chỉ chỉnh `llm/explanation_service.py` trong hàm `generate_explanation(...)`. Không tác động mô hình Bayesian hay UI.

## Kết quả
- Dù có hoặc không có API Gemini, hệ thống luôn trả về lời giải thích đúng định dạng 7 đoạn theo yêu cầu.