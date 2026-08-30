import numpy as np
from tqdm import tqdm
from sklearn.metrics import precision_recall_fscore_support, f1_score

from src.data.dataset_loader import load_saved_datasets
from src.utils.config import LABEL_COLUMNS
from src.utils.logger import get_logger

logger = get_logger(__name__)


def evaluate(model, thresholds=None):
    _, _, test_ds = load_saved_datasets()

    total_batches = sum(1 for _ in test_ds)

    y_true_list, y_pred_list = [], []
    for batch_x, batch_y in tqdm(
        test_ds, total=total_batches, desc="Predicting on test set"
    ):
        preds = model.predict(batch_x, verbose=0)
        y_true_list.append(batch_y.numpy())
        y_pred_list.append(preds)

    y_true = np.concatenate(y_true_list, axis=0)
    y_pred_prob = np.concatenate(y_pred_list, axis=0)

    if thresholds is None:
        thresholds = {label: 0.5 for label in LABEL_COLUMNS}

    y_pred = np.zeros_like(y_pred_prob, dtype=int)
    for i, label in enumerate(LABEL_COLUMNS):
        y_pred[:, i] = (y_pred_prob[:, i] >= thresholds[label]).astype(int)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    for i, label in enumerate(LABEL_COLUMNS):
        logger.info(
            f"{label}: precision={precision[i]:.3f} recall={recall[i]:.3f} f1={f1[i]:.3f}"
        )
    logger.info(f"Macro-F1: {macro_f1:.4f}")

    return {
        "per_class": dict(zip(LABEL_COLUMNS, zip(precision, recall, f1))),
        "macro_f1": macro_f1,
    }
