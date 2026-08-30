import os
import tensorflow as tf
from sklearn.model_selection import train_test_split

from src.data.preprocess import load_train_df, load_kaggle_test_df, encode_batch
from src.utils.config import (
    PROCESSED_DIR,
    LABEL_COLUMNS,
    VAL_SPLIT,
    RANDOM_SEED,
    BATCH_SIZE,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)
AUTOTUNE = tf.data.AUTOTUNE


def _make_dataset(input_ids, attention_mask, labels, shuffle=False):
    ds = tf.data.Dataset.from_tensor_slices(
        ({"input_ids": input_ids, "attention_mask": attention_mask}, labels)
    )
    if shuffle:
        ds = ds.shuffle(buffer_size=10000, seed=RANDOM_SEED)
    ds = ds.batch(BATCH_SIZE)
    ds = ds.cache()
    ds = ds.prefetch(AUTOTUNE)
    return ds


def build_datasets():
    df = load_train_df()
    labels = df[LABEL_COLUMNS].values.astype("float32")

    train_df, val_df, train_labels, val_labels = train_test_split(
        df, labels, test_size=VAL_SPLIT, random_state=RANDOM_SEED
    )

    test_df = load_kaggle_test_df()
    test_labels = test_df[LABEL_COLUMNS].values.astype("float32")

    train_ids, train_mask = encode_batch(train_df["comment_text"])
    val_ids, val_mask = encode_batch(val_df["comment_text"])
    test_ids, test_mask = encode_batch(test_df["comment_text"])

    train_ds = _make_dataset(train_ids, train_mask, train_labels, shuffle=True)
    val_ds = _make_dataset(val_ids, val_mask, val_labels)
    test_ds = _make_dataset(test_ids, test_mask, test_labels)

    return train_ds, val_ds, test_ds


def save_datasets(train_ds, val_ds, test_ds):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train_ds.save(os.path.join(PROCESSED_DIR, "train"))
    val_ds.save(os.path.join(PROCESSED_DIR, "val"))
    test_ds.save(os.path.join(PROCESSED_DIR, "test"))
    logger.info(f"Saved tf.data datasets to {PROCESSED_DIR}")


def load_saved_datasets():
    train_ds = tf.data.Dataset.load(os.path.join(PROCESSED_DIR, "train"))
    val_ds = tf.data.Dataset.load(os.path.join(PROCESSED_DIR, "val"))
    test_ds = tf.data.Dataset.load(os.path.join(PROCESSED_DIR, "test"))
    return train_ds, val_ds, test_ds


if __name__ == "__main__":
    train_ds, val_ds, test_ds = build_datasets()
    save_datasets(train_ds, val_ds, test_ds)
