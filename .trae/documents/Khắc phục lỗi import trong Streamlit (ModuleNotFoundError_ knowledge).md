## Nguyên nhân
- Khi chạy `streamlit run app/ui_streamlit.py`, Python thêm thư mục `app/` vào `sys.path` nhưng không thêm thư mục gốc dự án.
- `app/controller.py` import `knowledge.rule_engine`, nên cần `project_root` trong `sys.path`.

## Giải pháp tối ưu (ít thay đổi code)
- Chạy Streamlit từ thư mục gốc và đưa `project_root` vào `PYTHONPATH`:
  - `conda activate krr`
  - `cd "e:\CS 2022\Knowledge representation and reasoning\Final"`
  - `set PYTHONPATH=%CD%`
  - `python -m streamlit run app/ui_streamlit.py`

## Giải pháp mã hoá (ổn định, tự động)
- Chèn `project_root` vào `sys.path` ngay đầu `app/ui_streamlit.py` trước khi import:
```
import os, sys
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from app.controller import CreditController
```
- Không thay đổi các file khác; đảm bảo import `knowledge.*` hoạt động khi chạy từ bất cứ nơi nào.

## Xác minh
- Sau khi áp dụng một trong hai giải pháp:
  - Chạy: `python -m streamlit run app/ui_streamlit.py`
  - Form hiển thị; nhập dữ liệu; kết quả JSON gồm `facts`, `rule_conclusions`, `fired_rules`, `bayesian`, `final_class`.

Bạn chọn giải pháp. Nếu đồng ý phương án chèn `sys.path` vào `app/ui_streamlit.py`, tôi sẽ cập nhật ngay và xác minh chạy.