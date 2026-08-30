import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from django.conf import settings
import tensorflow as tf

_model = None
_thresholds = None
_tokenizer = None  # NEW: cache tokenizer too, same pattern as model

HF_REPO_ID = os.getenv("HF_MODEL_REPO", "samamazaid/sentinelai-distilbert")


def ensure_model_downloaded():
    """Download model + thresholds from Hugging Face Hub if not present locally."""
    from huggingface_hub import snapshot_download

    model_dir = Path(settings.MODEL_PATH)
    thresholds_path = Path(settings.THRESHOLDS_PATH)

    if model_dir.exists() and any(model_dir.iterdir()) and thresholds_path.exists():
        return

    print(
        f"Model not found locally — downloading from Hugging Face Hub ({HF_REPO_ID})..."
    )
    downloaded_path = Path(snapshot_download(repo_id=HF_REPO_ID))

    model_dir.parent.mkdir(parents=True, exist_ok=True)

    downloaded_saved_model = downloaded_path / "saved_model"
    if not model_dir.exists():
        import shutil

        shutil.copytree(downloaded_saved_model, model_dir)

    downloaded_thresholds = downloaded_path / "thresholds.json"
    if not thresholds_path.exists():
        import shutil

        thresholds_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(downloaded_thresholds, thresholds_path)

    print("Model download complete.")


def get_model():
    global _model
    if _model is None:
        print(
            "Loading TensorFlow SavedModel into memory..."
        )  # NEW: visibility in boot logs
        ensure_model_downloaded()
        _model = tf.saved_model.load(settings.MODEL_PATH)
        print("Model loaded.")  # NEW
    return _model


def get_thresholds():
    global _thresholds
    if _thresholds is None:
        ensure_model_downloaded()
        with open(settings.THRESHOLDS_PATH) as f:
            _thresholds = json.load(f)
    return _thresholds


def get_cached_tokenizer():  # NEW FUNCTION: reuse tokenizer instead of reloading every call
    global _tokenizer
    if _tokenizer is None:
        from src.data.preprocess import get_tokenizer

        print("Loading tokenizer...")
        _tokenizer = get_tokenizer()
        print("Tokenizer loaded.")
    return _tokenizer


def preload():  # NEW FUNCTION: single entrypoint for apps.py to call at worker boot
    """Called once at worker startup (via apps.py ready()) so the first
    real request doesn't pay the full load cost and risk timing out."""
    get_model()


def predict(text: str) -> dict:
    from src.data.preprocess import clean_text
    from src.utils.config import MAX_SEQ_LENGTH

    cleaned = clean_text(text)
    tokenizer = (
        get_cached_tokenizer()
    )  # CHANGED: was get_tokenizer() directly, now cached
    model = get_model()

    enc = tokenizer(
        [cleaned],
        padding="max_length",
        truncation=True,
        max_length=MAX_SEQ_LENGTH,
        return_tensors="np",
    )

    input_ids = tf.constant(enc["input_ids"], dtype=tf.int32)
    attention_mask = tf.constant(enc["attention_mask"], dtype=tf.int32)

    infer = model.signatures["serving_default"]
    output = infer(input_ids=input_ids, attention_mask=attention_mask)
    scores = list(output.values())[0].numpy()[0]

    return dict(zip(settings.LABEL_COLUMNS, [float(s) for s in scores]))


def apply_thresholds(scores: dict) -> dict:
    thresholds = get_thresholds()
    return {label: scores[label] >= thresholds.get(label, 0.5) for label in scores}
