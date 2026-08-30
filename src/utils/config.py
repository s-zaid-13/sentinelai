import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(Path(BASE_DIR) / ".env")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
TRAIN_CSV = os.path.join(RAW_DIR, "train.csv")
TEST_CSV = os.path.join(RAW_DIR, "test.csv")
TEST_LABELS_CSV = os.path.join(RAW_DIR, "test_labels.csv")

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

LABEL_COLUMNS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]

MAX_SEQ_LENGTH = 128
TOKENIZER_MODEL = "distilbert-base-uncased"

VAL_SPLIT = 0.1
RANDOM_SEED = 42
BATCH_SIZE = 32

THRESHOLD_LOW = 0.4
THRESHOLD_HIGH = 0.75

MODEL_DIR = os.path.join(BASE_DIR, "models")
CHECKPOINT_PATH = os.path.join(MODEL_DIR, "distilbert_checkpoint.weights.h5")
SAVED_MODEL_PATH = os.path.join(MODEL_DIR, "saved_model")
THRESHOLDS_PATH = os.path.join(MODEL_DIR, "thresholds.json")

BENCHMARK_SAMPLE_SIZE = int(os.getenv("BENCHMARK_SAMPLE_SIZE", 3))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
