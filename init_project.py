import os

folders = [
    "knowledge",
    "inference",
    "llm",
    "visualization",
    "app",
    "config",
    "reports",
    "reports/slides",
    "tests"
]

files = [
    "knowledge/model_structure.md",
    "knowledge/rules.py",
    "knowledge/rule_engine.py",

    "inference/bayesian_model.py",
    "inference/model.pkl",
    "inference/reasoning_manager.py",

    "llm/explanation_service.py",

    "visualization/causal_graph.py",
    "visualization/evaluation_plots.py",

    "app/ui_streamlit.py",
    "app/controller.py",
    "app/utils.py",

    "config/settings.py",

    "reports/technical_report.md",
    "reports/krr_description.md",
    "reports/rule_documentation.md",

    "tests/test_rules.py",
    "tests/test_forward_chaining.py",
    "tests/test_bayesian.py",

    "run.py",
    "requirements.txt"
]

# Tạo thư mục
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Tạo file rỗng
for file in files:
    with open(file, "w", encoding="utf-8") as f:
        pass

print("🎉 Hoàn tất khởi tạo cấu trúc dự án!")
