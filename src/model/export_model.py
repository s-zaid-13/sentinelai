import os
import shutil
from src.model.build_model import build_model
from src.utils.config import CHECKPOINT_PATH, SAVED_MODEL_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)


def export():
    # Clean any stray file/folder at the target path before exporting
    if os.path.exists(SAVED_MODEL_PATH):
        if os.path.isdir(SAVED_MODEL_PATH):
            shutil.rmtree(SAVED_MODEL_PATH)
        else:
            os.remove(SAVED_MODEL_PATH)
        logger.info(f"Cleared existing path: {SAVED_MODEL_PATH}")

    model = build_model()
    model.load_weights(CHECKPOINT_PATH)
    model.export(SAVED_MODEL_PATH)
    logger.info(f"Exported SavedModel to {SAVED_MODEL_PATH}")


if __name__ == "__main__":
    export()
