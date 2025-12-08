## Mục Tiêu
- Thay thế nội dung prompt dùng cho Gemini bằng mẫu bạn cung cấp, chỉ dựa trên `facts`.

## Thay Đổi Kỹ Thuật
- Sửa `llm/explanation_service.py` trong hàm `build_prompt(...)` để:
  - Tạo biến `facts_json` từ `facts` (`json.dumps(..., ensure_ascii=False)`).
  - Chèn đúng nội dung 7 đoạn và yêu cầu văn phong như bạn mô tả.
  - Loại bỏ phần chèn `rule_conclusions`, `fired_rules`, `bayes_output`, `final_class` khỏi prompt để bám đúng yêu cầu.

## Phạm Vi
- Chỉ sửa `build_prompt(...)`; giữ nguyên `call_gemini(...)` và luồng `generate_explanation(...)`.

## Kiểm Tra
- Gọi thử `build_prompt` với dữ liệu mẫu để xác nhận cấu trúc và nội dung khớp 7 đoạn.
- Không cần train lại Bayesian; thay đổi prompt không ảnh hưởng mô hình.

## Kết Quả
- Gemini nhận prompt đúng định dạng 7 đoạn, trình bày rõ ràng theo yêu cầu, sử dụng dữ liệu `facts` đã xử lý từ hệ thống.