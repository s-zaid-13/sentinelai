import numpy as np
from tqdm import tqdm
from sklearn.metrics import f1_score

from src.model.build_model import build_model
from src.data.dataset_loader import load_saved_datasets
from src.utils.config import LABEL_COLUMNS, CHECKPOINT_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_val_predictions():
    _, val_ds, _ = load_saved_datasets()
    model = build_model()
    model.load_weights(CHECKPOINT_PATH)

    # count batches first so tqdm shows a proper total (val set is known, ~499 batches)
    total_batches = sum(1 for _ in val_ds)

    y_true_list, y_pred_list = [], []
    for batch_x, batch_y in tqdm(
        val_ds, total=total_batches, desc="Predicting on val set"
    ):
        preds = model.predict(batch_x, verbose=0)
        y_true_list.append(batch_y.numpy())
        y_pred_list.append(preds)

    y_true = np.concatenate(y_true_list, axis=0)
    y_pred_prob = np.concatenate(y_pred_list, axis=0)
    return y_true, y_pred_prob


def find_best_thresholds(y_true, y_pred_prob, thresholds=np.arange(0.1, 0.95, 0.05)):
    best_thresholds = {}
    for label_idx, label in enumerate(tqdm(LABEL_COLUMNS, desc="Tuning thresholds")):
        best_f1 = 0
        best_t = 0.5
        for t in thresholds:
            preds = (y_pred_prob[:, label_idx] >= t).astype(int)
            f1 = f1_score(y_true[:, label_idx], preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_t = t
        best_thresholds[label] = round(float(best_t), 2)
        logger.info(f"{label}: best_threshold={best_t:.2f} val_f1={best_f1:.3f}")
    return best_thresholds


if __name__ == "__main__":
    y_true, y_pred_prob = get_val_predictions()
    thresholds = find_best_thresholds(y_true, y_pred_prob)
    print("\nFinal per-class thresholds:", thresholds)
