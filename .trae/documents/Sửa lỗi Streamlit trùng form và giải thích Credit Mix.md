## Nguyên nhân lỗi
- `app/ui_streamlit.py` có 2 khối tạo form khác nhau, cả hai dùng `st.form("credit_form")` → trùng `key` sinh lỗi.
- File còn bị trùng import và logic hiển thị (hai giao diện trong cùng file).

## Cách sửa
- Giữ lại giao diện chính phía trên (đã tiếng Việt, có đầy đủ phần hiển thị), xoá khối thứ hai từ dòng 98–128.
- Đảm bảo chỉ còn 1 form duy nhất với `key='credit_form'`.
- Giữ `sys.path` injection và `from app.controller import CreditController` như hiện tại.

## Giải thích Credit Mix
- `credit_mix` là đặc trưng đầu vào từ dataset (loại hình tín dụng: thẻ, vay thế chấp, vay tiêu dùng…).
- Mô hình Bayes dùng `OneHotEncoder` trên `credit_mix` để học; tập luật dùng `credit_mix` để suy luận `credit_mix_quality`.
- Vì vậy, trường này là INPUT của form người dùng. Không phải kết quả của model hay rule. Nếu bạn muốn tự động hoá, cần thêm logic đánh giá credit mix từ danh mục tài khoản tín dụng.

## Xác minh sau sửa
- Chạy `python -m streamlit run app/ui_streamlit.py` sẽ không còn lỗi form trùng.
- Submit form trả về kết quả như trước: `final_class`, `bayesian`, `fired_rules`, `rule_conclusions`, `facts`.

Bạn xác nhận để tôi xoá khối form trùng và chuẩn hoá file UI?