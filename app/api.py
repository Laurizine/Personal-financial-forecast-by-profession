from fastapi import FastAPI
from app.controller import CreditController

app = FastAPI()
controller = CreditController()

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
