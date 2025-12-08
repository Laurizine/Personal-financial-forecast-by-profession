import os

ROOT = os.path.dirname(os.path.dirname(__file__))
DATASET_PATH = os.path.join(ROOT, "Dataset", "simulated_data.csv")
MODEL_PATH = os.path.join(ROOT, "inference", "model.pkl")
