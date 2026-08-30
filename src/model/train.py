import os
import tensorflow as tf
import wandb
from wandb.integration.keras import WandbMetricsLogger

from src.data.preprocess import load_train_df
from src.data.dataset_loader import load_saved_datasets
from src.model.build_model import build_model
from src.utils.config import LABEL_COLUMNS, MODEL_DIR, CHECKPOINT_PATH
from src.utils.logger import get_logger
import shutil

logger = get_logger(__name__)


def compute_pos_weights(df, max_weight=15.0):
    weights = []
    for col in LABEL_COLUMNS:
        pos = df[col].sum()
        neg = len(df) - pos
        raw_weight = neg / max(pos, 1)
        capped_weight = min(raw_weight, max_weight)
        weights.append(capped_weight)
    logger.info(
        f"Per-class pos_weight (capped at {max_weight}): {dict(zip(LABEL_COLUMNS, weights))}"
    )
    return tf.constant(weights, dtype=tf.float32)


def focal_loss(pos_weights, gamma=2.0, label_smoothing=0.05):
    def loss_fn(y_true, y_pred):
        y_true = y_true * (1 - label_smoothing) + 0.5 * label_smoothing
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1 - 1e-7)

        pt = tf.where(tf.equal(tf.round(y_true), 1), y_pred, 1 - y_pred)
        weight = tf.where(tf.equal(tf.round(y_true), 1), pos_weights, 1.0)

        loss = -weight * tf.pow(1 - pt, gamma) * tf.math.log(pt)
        return tf.reduce_mean(loss)

    return loss_fn


def train(epochs=2, batch_size=32, peak_lr=2e-5):
    wandb.init(
        project="sentinelai",
        config={
            "max_seq_length": 128,
            "batch_size": batch_size,
            "epochs": epochs,
            "loss": "focal_loss",
            "pos_weight_cap": 15.0,
        },
    )

    train_ds, val_ds, _ = load_saved_datasets()
    pos_weights = compute_pos_weights(load_train_df())

    train_steps_per_epoch = sum(1 for _ in train_ds)

    lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=peak_lr,
        decay_steps=train_steps_per_epoch * epochs,
        warmup_target=peak_lr,
        warmup_steps=int(train_steps_per_epoch * 0.5),
    )

    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
        loss=focal_loss(pos_weights),
        metrics=[tf.keras.metrics.AUC(name="auc", multi_label=True)],
    )

    callbacks = [
        WandbMetricsLogger(),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", mode="min", patience=2, restore_best_weights=True
        ),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_weights(CHECKPOINT_PATH)
    logger.info(f"Saved checkpoint to {CHECKPOINT_PATH}")

    return model


if __name__ == "__main__":
    train()
