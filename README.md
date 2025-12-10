# Hệ thống Chuyên gia Đánh giá Tín dụng (Credit Scoring Expert System)

Hệ thống lai (Hybrid AI) kết hợp **Luật chuyên gia (Rule-based)**, **Mô hình Bayesian (Machine Learning)** và **Mô hình Ngôn ngữ lớn (LLM - Gemini)** để phân tích rủi ro tín dụng, đưa ra quyết định phân loại và giải thích chi tiết bằng tiếng Việt.

## 🚀 Công nghệ & Phương pháp

*   **Giao diện (UI):** `Streamlit` (Tương tác trực quan, cache thông minh)
*   **API Service:** `FastAPI` (Cung cấp RESTful API hiệu năng cao)
*   **Machine Learning:** `Scikit-learn` (Gaussian Naive Bayes, Pipeline chuẩn hóa)
*   **LLM:** `Google Gemini` (Tạo giải thích tự nhiên, hỗ trợ `gemini-2.0-flash-lite` và `gemini-2.5-flash`)
*   **Suy diễn:** Forward-chaining Rule Engine (Máy suy diễn tiến)

## 📂 Cấu trúc Dự án

```text
├── app/
│   ├── ui_streamlit.py      # Giao diện Web (Streamlit)
│   ├── api.py               # REST API (FastAPI)
│   └── controller.py        # Bộ điều khiển trung tâm (Logic chính)
├── knowledge/
│   ├── rules.py             # Tập luật nghiệp vụ (Business Rules)
│   └── rule_engine.py       # Máy suy diễn (Inference Engine)
├── inference/
│   ├── bayesian_model.py    # Mô hình học máy (GaussianNB)
│   └── model.pkl            # File mô hình đã huấn luyện
├── llm/
│   └── explanation_service.py # Tích hợp Google Gemini (Prompting & Validation)
├── env/
│   └── set_gemini.ps1       # Script cấu hình môi trường (API Key & Model)
├── Dataset/                 # Dữ liệu huấn luyện
├── tests/                   # Bộ kiểm thử (Unit & Integration Tests)
├── run.py                   # CLI Tools (Train/Predict)
└── requirements.txt         # Các thư viện phụ thuộc
```

## 🛠️ Cài đặt & Cấu hình

### 1. Cài đặt thư viện
Yêu cầu Python 3.10+.
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Gemini (Quan trọng)
Sử dụng script PowerShell để thiết lập API Key và Model.
*   **Mặc định:** Model là `gemini-2.0-flash-lite` (nhanh, tiết kiệm).
*   **Tùy chọn:** Có thể chuyển sang `gemini-2.5-flash`.

```powershell
# Cho phép chạy script (nếu chưa mở)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Cấu hình mặc định (gemini-2.0-flash-lite)
.\env\set_gemini.ps1 -API_KEY "YOUR_GOOGLE_API_KEY"

# Hoặc chỉ định model khác
.\env\set_gemini.ps1 -API_KEY "YOUR_GOOGLE_API_KEY" -MODEL "gemini-2.5-flash"
```
> **Lưu ý:** Hệ thống chỉ chấp nhận các model trong whitelist (`gemini-2.0-flash-lite`, `gemini-2.5-flash`).

## ▶️ Hướng dẫn Chạy Hệ thống

### Cách 1: Giao diện Web (Khuyên dùng)
Chạy ứng dụng Streamlit với giao diện Giáng sinh thân thiện:
```bash
streamlit run app/ui_streamlit.py
```
*   Truy cập: `http://localhost:8501`

### Cách 2: REST API (FastAPI)
Khởi chạy server backend để tích hợp với các hệ thống khác:
```bash
uvicorn app.api:app --reload --port 8000
```
*   **Docs (Swagger UI):** `http://localhost:8000/docs`
*   **Endpoint chính:** `POST /explain`

### Cách 3: Command Line (CLI)
Huấn luyện lại mô hình hoặc dự đoán nhanh:
```bash
# Huấn luyện mô hình Bayesian
python run.py train

# Dự đoán mẫu
python run.py predict --input '{"income_monthly": 20000000, "debt_amount": 5000000, ...}'
```

## 🧪 Kiểm thử (Testing)
Chạy bộ test suite để đảm bảo hệ thống hoạt động ổn định:
```bash
python -m pytest tests
```
Bao gồm các test case:
*   End-to-End Controller
*   Bayesian Stability
*   Rule Logic & Coverage
*   Input Normalization
