import argparse
import json
import logging
from config.settings import DATASET_PATH
from inference.bayesian_model import BayesianModel
from knowledge.rules import infer_from_user_input

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["train", "predict"])
    parser.add_argument("--input", dest="input", help="JSON string or path to JSON file", default=None)
    args = parser.parse_args()

    if args.command == "train":
        m = BayesianModel()
        m.train(DATASET_PATH)
        print("Đã huấn luyện mô hình xong và lưu vào model.pkl")
        return

    if args.command == "predict":
        if not args.input:
            raise SystemExit("--input required")
        try:
            if args.input.endswith(".json"):
                with open(args.input, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            else:
                payload = json.loads(args.input)
        except Exception as e:
            raise SystemExit(f"Invalid input: {e}")

        m = BayesianModel()
        rule_result = infer_from_user_input(payload)
        bayes_result = m.predict(rule_result["facts"]) if isinstance(rule_result, dict) else {}
        print(json.dumps({"rules": rule_result, "bayes": bayes_result}, ensure_ascii=False))

if __name__ == "__main__":
    main()
