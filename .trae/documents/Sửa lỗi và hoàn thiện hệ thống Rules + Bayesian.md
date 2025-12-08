## Đánh giá hiện trạng
- Cấu trúc thư mục đã có đầy đủ: `knowledge/`, `inference/`, `app/`, `llm/`, `tests/`, `Dataset/`, `config/`, nhưng nhiều file rỗng.
- `knowledge/rules.py` chứa rule và các hàm suy luận, nhưng phần cuối bị trùng lặp và có dấu hiệu cắt cụt (lặp `_mix`, `_safe_ratio`, `apply_rules`, `infer_from_user_input` 2 lần, đoạn `else:` chưa đóng) → có nguy cơ SyntaxError.
- `knowledge/rule_engine.py:1` dùng `from rules import rules` thay vì `from knowledge.rules import rules` → dễ lỗi import khi chạy từ ngoài thư mục.
- `inference/bayesian_model.py` ổn về pipeline, nhưng:
  - `OneHotEncoder` thiếu `sparse=False`/`sparse_output=False` (dòng 59) → GaussianNB không nhận `sparse`.
  - Đường dẫn model/dataset đang hard-code tuyệt đối (`E:\...`) → kém linh hoạt.
  - `predict` truy xuất trực tiếp key có thể gây `KeyError`, và không tự tính lại `ratio` nếu thiếu.
- `app/controller.py` đã nối RuleEngine + BayesianModel + LLM; tốt, nhưng phụ thuộc import gói chuẩn.
- `tests/` hầu hết rỗng; `tests/test_bayesian.py:1` import sai (`from bayesian_model import ...`).
- Không có `__init__.py` trong các thư mục gói → import dạng `package.module` có thể thất bại.
- `requirements.txt`, `run.py`, `app/ui_streamlit.py`, `config/settings.py` rỗng → chưa có entrypoint/UI/cấu hình.

## Kế hoạch sửa lỗi & hoàn thiện
### 1) Ổn định import và cấu trúc gói
- Thêm `__init__.py` vào các thư mục: `knowledge/`, `inference/`, `app/`, `llm/`, `tests/`, `visualization/`, `config/`.
- Sửa `knowledge/rule_engine.py:1` dùng `from knowledge.rules import rules`.

### 2) Làm sạch `knowledge/rules.py`
- Gỡ các đoạn trùng lặp, hoàn thiện `infer_from_user_input` (đảm bảo đóng khối `else`), giữ một phiên bản duy nhất của `_mix`, `_safe_ratio`, `apply_rules`, `infer_from_user_input`.
- Xác nhận danh sách `rules` không lỗi cú pháp và suy diễn forward-chaining chạy đúng.

### 3) Cứng hoá `inference/bayesian_model.py`
- `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` (hoặc `sparse=False` tuỳ version sklearn) để đầu ra dense.
- Trong `predict`, dùng `.get()` và tự tính `income_expense_ratio`/`debt_ratio` nếu thiếu; tránh `KeyError`.
- Tách đường dẫn sang `config/settings.py` (ví dụ `DATASET_PATH`, `MODEL_PATH`) và dùng đường dẫn tương đối.

### 4) Hoàn thiện cấu hình & phụ thuộc
- Điền `requirements.txt` (pandas, numpy, scikit-learn, streamlit – nếu dùng UI).
- `config/settings.py`: đặt hằng số đường dẫn tương đối.

### 5) Entry points để chạy nhanh
- `run.py`: cung cấp CLI `train` (đọc dataset, lưu model) và `predict` (nhận JSON, chạy rules + bayes, in kết quả).
- Tuỳ chọn: `app/ui_streamlit.py` form nhập liệu (nghề, thu nhập, chi tiêu, nợ, trả chậm, lịch sử, tài khoản mới, credit mix), hiển thị kết quả rule + bayes + giải thích.

### 6) Bổ sung kiểm thử
- Sửa `tests/test_bayesian.py` import đúng: `from inference.bayesian_model import BayesianModel`.
- Viết test đơn giản cho forward-chaining (tạo facts mẫu, kỳ vọng `overall_risk` và `rule_credit_class`).

### 7) Xác minh chạy end-to-end
- Chạy `train` trên `Dataset/simulated_data.csv`.
- Chạy `predict` với payload mẫu, xác nhận kết quả `final_class`, `fired_rules`, `bayes_score`.

## Kết quả mong đợi
- Hệ thống chạy ổn định: nhận input người dùng, suy diễn theo rule, dự đoán bằng Naive Bayes, hợp nhất kết quả và sinh lời giải thích.
- Không còn lỗi import/cú pháp, pipeline sklearn chạy với đầu ra dense, không phụ thuộc đường dẫn tuyệt đối.

Bạn xác nhận để tôi tiến hành sửa và bổ sung các phần trên?