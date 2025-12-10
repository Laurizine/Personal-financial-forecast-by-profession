# Hệ thống Chuyên gia Đánh giá Tín dụng (Credit Scoring Expert System)

Hệ thống lai (Hybrid AI) kết hợp **Luật chuyên gia (Rule-based)**, **Mô hình Bayesian (Machine Learning)** và **Mô hình Ngôn ngữ lớn (LLM - Gemini)** để phân tích rủi ro tín dụng, đưa ra quyết định phân loại và giải thích chi tiết bằng tiếng Việt.

## 🚀 Công nghệ & Phương pháp

- **Giao diện (UI):** `Streamlit` (tương tác trực quan, cache thông minh, throttle)
- **API Service:** `FastAPI` (cung cấp RESTful API hiệu năng cao)
- **Machine Learning:** `Scikit-learn` (Gaussian Naive Bayes, Pipeline chuẩn hóa)
- **LLM:** `Google Gemini` (tạo giải thích tự nhiên, khuyên dùng `gemini-2.0-flash-lite`, có thể dùng `gemini-2.5-flash`)
- **Suy diễn:** Forward-chaining Rule Engine (máy suy diễn tiến)

## 📂 Cấu trúc Dự án

```text
├── .streamlit/
│   └── config.toml              # Tắt auto-rerun, ổn định UI
├── app/
│   ├── ui_streamlit.py          # Giao diện Web (Streamlit)
│   ├── api.py                   # REST API (FastAPI)
│   ├── controller.py            # Bộ điều khiển trung tâm (Logic chính)
│   └── utils.py                 # Tiện ích dùng chung (nếu cần)
├── config/
│   └── settings.py              # Đường dẫn dữ liệu/mô hình
├── knowledge/
│   ├── rules.py                 # Tập luật nghiệp vụ (Business Rules)
│   ├── rule_engine.py           # Máy suy diễn (Inference Engine)
│   └── model_structure.md       # Mô tả cấu trúc mô hình/tri thức
├── inference/
│   ├── bayesian_model.py        # Mô hình học máy (GaussianNB)
│   ├── model.pkl                # File mô hình đã huấn luyện
│   └── reasoning_manager.py     # (Dự phòng/khung quản lý suy luận)
├── llm/
│   └── explanation_service.py   # Tích hợp Gemini (Prompting, gọi API, cache)
├── env/
│   ├── set_gemini.ps1           # Thiết lập API Key và Model
│   └── clear_env.ps1            # Xóa biến môi trường Gemini
├── tests/                       # Bộ kiểm thử (Unit & Integration Tests)
│   ├── test_api.py
│   ├── test_bayesian.py
│   ├── test_bayesian_stability.py
│   ├── test_edge_cases.py
│   ├── test_end_to_end.py
│   ├── test_fact_normalization.py
│   ├── test_forward_chaining.py
│   ├── test_llm_cache.py        # Kiểm tra cache lời giải thích LLM
│   ├── test_llm_fallback.py     # Kiểm tra fallback khi LLM lỗi
│   ├── test_rule_coverage.py
│   └── test_rules.py
├── visualization/
│   ├── causal_graph.py          # Quan hệ nhân quả
│   └── evaluation_plots.py      # Biểu đồ đánh giá
├── reports/
│   ├── krr_description.md
│   ├── rule_documentation.md
│   └── technical_report.md
├── Dataset/
│   ├── simulated_data.csv
│   └── simulated_data.ipynb
├── run.py                       # CLI Tools (Train/Predict)
├── requirements.txt             # Thư viện phụ thuộc
└── README.md                    # Tài liệu dự án
```

## 🛠️ Cài đặt & Cấu hình

### 1. Cài đặt thư viện
Yêu cầu Python 3.10+.
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Gemini (Quan trọng)
Thiết lập API Key và Model bằng PowerShell:
```powershell
# Cho phép chạy script (nếu chưa mở)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Cấu hình mặc định (gemini-2.0-flash-lite)
./env/set_gemini.ps1 -API_KEY "YOUR_GOOGLE_API_KEY"

# Hoặc chỉ định model khác
./env/set_gemini.ps1 -API_KEY "YOUR_GOOGLE_API_KEY" -MODEL "gemini-2.5-flash"

# Xóa biến môi trường Gemini (nếu cần)
./env/clear_env.ps1
```

### 3. Cấu hình Streamlit chống auto-rerun (Khuyến nghị)
Đã cấu hình sẵn tại `.streamlit/config.toml`:
```toml
[server]
fileWatcherType = "none"
runOnSave = false
```

## ▶️ Hướng dẫn Chạy Hệ thống

### Cách 1: Giao diện Web (Khuyên dùng)
```bash
streamlit run app/ui_streamlit.py
```
- Truy cập: `http://localhost:8501`

### Cách 2: REST API (FastAPI)
```bash
uvicorn app.api:app --reload --port 8000
```
- Docs (Swagger UI): `http://localhost:8000/docs`
- Endpoint chính: `POST /explain`

### Cách 3: Command Line (CLI)
```bash
# Huấn luyện mô hình Bayesian
python run.py train

# Dự đoán mẫu
python run.py predict --input '{"income_monthly": 20000000, "debt_amount": 5000000, ...}'
```

## 🔒 Chính sách gọi LLM & Chống spam

- Retry hợp lý: chỉ thử lại khi lỗi mạng (ví dụ: mất kết nối). Không thử lại với lỗi rate-limit 429/ResourceExhausted.
- Cache nhiều tầng:
  - UI: `st.cache_data` cho kết quả tính toán theo input.
  - Controller: cache nội bộ `_explain_cache` cho lời giải thích LLM.
  - LLM: cache instance `GenerativeModel` theo cặp `GOOGLE_API_KEY` + `GEMINI_MODEL`.
- Throttle UI: kiểm soát tần suất gọi qua biến `LLM_MIN_INTERVAL_SEC` để tránh spam liên tiếp.

## 🌱 Biến môi trường

- `GOOGLE_API_KEY`: API key của Google Gemini.
- `GEMINI_MODEL`: Tên model Gemini (khuyên dùng `gemini-2.0-flash-lite`, có thể `gemini-2.5-flash`).
- `LLM_MIN_INTERVAL_SEC`: Khoảng cách tối thiểu (giây) giữa 2 lần gọi UI (mặc định: `5`).

## 🧪 Kiểm thử (Testing)

Chạy bộ test:
```bash
python -m pytest tests
```
Nhóm test tiêu biểu:
- End-to-End Controller
- Bayesian Stability
- Rule Logic & Coverage
- Forward Chaining
- Fact Normalization
- API
- LLM Cache/Retry/Fallback

## ⚡ Gợi ý hiệu năng & Khắc phục sự cố

- Khuyến nghị dùng `st.cache_resource` cho instance `CreditController` để tránh tải lại mô hình và giữ cache nội bộ khi UI rerun.
- Không commit API key; dùng script `env/set_gemini.ps1` và `env/clear_env.ps1` để quản lý key.
- Nếu gặp lỗi mạng, thử lại sau vài giây; nếu gặp rate-limit 429, chờ tăng quota hoặc giảm tần suất gọi.
