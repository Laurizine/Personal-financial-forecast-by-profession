from fastapi import FastAPI
import os, sys, time
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from app.controller import CreditController
from app.utils import RateLimitFilter
import logging

level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

try:
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
except Exception:
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

rate_window = float(os.environ.get("LOG_RATE_WINDOW", "5"))
rate_max = int(os.environ.get("LOG_RATE_MAX", "3"))
rate_filter = RateLimitFilter(window_seconds=rate_window, max_records=rate_max)
stream_handler.addFilter(rate_filter)
file_handler.addFilter(rate_filter)

root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.setLevel(level)
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)
logger = logging.getLogger(__name__)

app = FastAPI()
controller = CreditController()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/explain")
def explain(payload: dict):
    try:
        job = payload.get("job") if isinstance(payload, dict) else None
        logger.debug(f"/explain payload keys: {list(payload.keys()) if isinstance(payload, dict) else None}")
        logger.info(f"/explain received: job={job}")
    except Exception:
        pass
    result = controller.process(payload)
    try:
        final_class = result.get("final_class")
        exp_len = len(result.get("llm_explanation", ""))
        logger.info(f"/explain responded: final_class={final_class}, explanation_len={exp_len}")
    except Exception:
        pass
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
