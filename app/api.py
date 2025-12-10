from fastapi import FastAPI
import os, sys
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from app.controller import CreditController

app = FastAPI()
controller = CreditController()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/explain")
def explain(payload: dict):
    result = controller.process(payload)
    return {
        "final_class": result["final_class"],
        "bayesian": result["bayesian"],
        "rule_conclusions": result["rule_conclusions"],
        "fired_rules": result["fired_rules"],
        "facts": result["facts"],
        "explanation": result["llm_explanation"],
    }

if __name__ == "__main__":
    print("FastAPI app is defined as 'app'. Vui lòng chạy bằng môi trường tích hợp hoặc bỏ qua nếu không dùng API.")
