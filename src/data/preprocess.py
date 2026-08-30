import re
import numpy as np
import tensorflow as tf
import pandas as pd

from src.utils.config import (
    TRAIN_CSV,
    TEST_CSV,
    TEST_LABELS_CSV,
    LABEL_COLUMNS,
    TOKENIZER_MODEL,
    MAX_SEQ_LENGTH,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

_tokenizer = None


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
    return _tokenizer


def clean_text(text: str) -> str:
    text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[^a-z0-9!?.,'\" ]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def load_train_df() -> pd.DataFrame:
    logger.info(f"Loading {TRAIN_CSV}")
    df = pd.read_csv(TRAIN_CSV)
    df["comment_text"] = df["comment_text"].apply(clean_text)

    before = len(df)
    df = df[df["comment_text"].str.strip() != ""]
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} train rows that became empty after cleaning")

    return df


def load_kaggle_test_df() -> pd.DataFrame:
    logger.info(f"Loading {TEST_CSV} and {TEST_LABELS_CSV}")
    test_df = pd.read_csv(TEST_CSV)
    labels_df = pd.read_csv(TEST_LABELS_CSV)
    merged = test_df.merge(labels_df, on="id")
    merged = merged[~(merged[LABEL_COLUMNS] == -1).any(axis=1)]
    merged["comment_text"] = merged["comment_text"].apply(clean_text)

    before = len(merged)
    merged = merged[merged["comment_text"].str.strip() != ""]
    dropped = before - len(merged)
    if dropped > 0:
        logger.info(f"Dropped {dropped} test rows that became empty after cleaning")

    logger.info(f"Usable scored test rows: {len(merged)}")
    return merged


def encode_batch(texts, chunk_size: int = 2000):
    """
    Tokenizes text in chunks to avoid huge memory allocation, and returns
    TensorFlow tensors. return_tensors="tf" is no longer supported by the
    installed tokenizer backend (only pt/np/mlx), so we encode to numpy
    and convert to tf.constant manually.
    """
    tokenizer = get_tokenizer()
    texts = list(texts)

    all_input_ids = []
    all_attention_mask = []

    for i in range(0, len(texts), chunk_size):
        chunk = texts[i : i + chunk_size]
        enc = tokenizer(
            chunk,
            padding="max_length",
            truncation=True,
            max_length=MAX_SEQ_LENGTH,
            return_tensors="np",
        )
        all_input_ids.append(enc["input_ids"])
        all_attention_mask.append(enc["attention_mask"])

        if (i // chunk_size) % 10 == 0:
            logger.info(f"Encoded {i + len(chunk)}/{len(texts)} texts")

    input_ids_np = np.concatenate(all_input_ids, axis=0)
    attention_mask_np = np.concatenate(all_attention_mask, axis=0)

    input_ids_tf = tf.constant(input_ids_np, dtype=tf.int32)
    attention_mask_tf = tf.constant(attention_mask_np, dtype=tf.int32)

    return input_ids_tf, attention_mask_tf
