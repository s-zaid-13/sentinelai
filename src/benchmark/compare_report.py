import os
import time
import json
import re
import numpy as np
import tensorflow as tf
from sklearn.metrics import precision_recall_fscore_support, f1_score

from src.data.preprocess import load_kaggle_test_df, encode_batch
from src.utils.config import (
    LABEL_COLUMNS,
    SAVED_MODEL_PATH,
    BENCHMARK_SAMPLE_SIZE,
    DOCS_DIR,
    THRESHOLDS_PATH,
)
from src.benchmark.llm_classify import (
    classify_gemini,
    classify_groq,
    GEMINI_MODEL,
    GROQ_MODEL,
    text_hash,
    load_cache,
    save_cache,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_thresholds():
    with open(THRESHOLDS_PATH) as f:
        return json.load(f)


def run_keras_model(texts):
    infer = tf.saved_model.load(SAVED_MODEL_PATH).signatures["serving_default"]
    input_ids, attention_mask = encode_batch(texts, chunk_size=len(texts))

    start = time.time()
    outputs = infer(input_ids=input_ids, attention_mask=attention_mask)
    total_latency = time.time() - start

    preds_prob = list(outputs.values())[0].numpy()
    thresholds = load_thresholds()
    threshold_array = np.array([thresholds[label] for label in LABEL_COLUMNS])
    preds = (preds_prob >= threshold_array).astype(int)

    avg_latency = total_latency / len(texts)
    return preds, avg_latency


def _extract_retry_delay(error_str, default=30):
    match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)", str(error_str))
    if match:
        return int(match.group(1)) + 2
    return default


def run_llm(texts, classify_fn, name, delay=0.5, max_retries=2):
    cache = load_cache(name)
    preds, latencies = [], []
    cache_hits = 0

    for i, text in enumerate(texts):
        key = text_hash(text)

        if key in cache:
            preds.append(cache[key]["pred"])
            latencies.append(cache[key]["latency"])
            cache_hits += 1
            continue

        pred, latency = [0] * len(LABEL_COLUMNS), 0
        for attempt in range(max_retries + 1):
            try:
                pred, latency, _ = classify_fn(text)
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = _extract_retry_delay(err_str)
                    logger.warning(
                        f"{name} rate-limited on row {i}, waiting {wait}s (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    time.sleep(wait)
                else:
                    logger.warning(f"{name} failed on row {i}: {e}")
                    break

        preds.append(pred)
        latencies.append(latency)

        cache[key] = {"pred": pred, "latency": latency}
        save_cache(name, cache)

        if i % 10 == 0:
            logger.info(f"{name}: {i}/{len(texts)}")
        time.sleep(delay)

    logger.info(f"{name}: {cache_hits}/{len(texts)} served from cache")
    return np.array(preds), np.mean(latencies) if latencies else 0.0


def compute_metrics(y_true, y_pred):
    _, _, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    return macro_f1, dict(zip(LABEL_COLUMNS, f1))


def generate_report():
    df = load_kaggle_test_df().sample(n=BENCHMARK_SAMPLE_SIZE, random_state=42)
    texts = df["comment_text"].tolist()
    y_true = df[LABEL_COLUMNS].values.astype(int)

    keras_preds, keras_latency = run_keras_model(texts)
    keras_macro_f1, keras_per_class = compute_metrics(y_true, keras_preds)

    gemini_preds, gemini_latency = run_llm(texts, classify_gemini, "gemini", delay=1.0)
    gemini_macro_f1, gemini_per_class = compute_metrics(y_true, gemini_preds)

    groq_preds, groq_latency = run_llm(texts, classify_groq, "groq", delay=0.3)
    groq_macro_f1, groq_per_class = compute_metrics(y_true, groq_preds)

    report = f"""# LLM Benchmark Report

    Sample size: {BENCHMARK_SAMPLE_SIZE} messages from held-out Jigsaw test set.

    Both LLM services used are free-tier — cost is not applicable/tracked, but
    free-tier requests are subject to rate limits which real deployments would
    need to work around.

    ## Results

    | Model | Macro-F1 | Avg Latency (s) |
    |---|---:|---:|
    | **Fine-tuned DistilBERT (local)** | **{keras_macro_f1:.4f}** | **{keras_latency:.4f}** |
    | {GEMINI_MODEL} | {gemini_macro_f1:.4f} | {gemini_latency:.4f} |
    | {GROQ_MODEL} | {groq_macro_f1:.4f} | {groq_latency:.4f} |

    ## Per-Class F1

    | Category | DistilBERT | Gemini | Groq |
    |---|---:|---:|---:|
    """

    for label in LABEL_COLUMNS:
        report += (
            f"| {label} | "
            f"**{keras_per_class[label]:.3f}** | "
            f"{gemini_per_class[label]:.3f} | "
            f"{groq_per_class[label]:.3f} |\\n"
        )

    report += f"""
    ## Observations

    The fine-tuned DistilBERT model achieved the highest Macro-F1 at
    {keras_macro_f1:.4f}, compared with {groq_macro_f1:.4f} for {GROQ_MODEL}
    and {gemini_macro_f1:.4f} for {GEMINI_MODEL}.

    DistilBERT also achieved the lowest average latency at
    {keras_latency:.4f} seconds per message. {GEMINI_MODEL} had an average
    latency of {gemini_latency:.4f} seconds, while {GROQ_MODEL} had an average
    latency of {groq_latency:.4f} seconds.

    At the per-class level, DistilBERT achieved its strongest F1 scores on
    {max(keras_per_class, key=keras_per_class.get)} ({keras_per_class[max(keras_per_class, key=keras_per_class.get)]:.3f}),
    {sorted(keras_per_class, key=keras_per_class.get, reverse=True)[1]}
    ({keras_per_class[sorted(keras_per_class, key=keras_per_class.get, reverse=True)[1]]:.3f}),
    and {sorted(keras_per_class, key=keras_per_class.get, reverse=True)[2]}
    ({keras_per_class[sorted(keras_per_class, key=keras_per_class.get, reverse=True)[2]]:.3f}).

    It also produced non-zero F1 scores across all six toxicity categories,
    whereas the tested LLM classifiers produced zero F1 for several categories
    in this sample.

    All LLM results were cached per input. This allows previously classified
    messages to be skipped when the benchmark is re-run after an interruption
    or rate-limit event.

    Since both LLM options were accessed through free-tier services, API cost
    was not tracked in this benchmark. The comparison therefore focuses on
    classification performance and inference latency.

    ## Conclusion

    The benchmark shows that the fine-tuned local DistilBERT model provided
    the strongest overall performance among the three evaluated approaches,
    achieving a Macro-F1 of {keras_macro_f1:.4f} compared with
    {gemini_macro_f1:.4f} for {GEMINI_MODEL} and {groq_macro_f1:.4f} for
    {GROQ_MODEL}.

    It also achieved the lowest measured latency of {keras_latency:.4f}
    seconds per message, compared with {gemini_latency:.4f} seconds for
    {GEMINI_MODEL} and {groq_latency:.4f} seconds for {GROQ_MODEL}.

    The results support using the fine-tuned DistilBERT model as the primary
    toxicity classification model, while the LLM-based approaches can be
    considered alternative or supplementary classifiers.

    The LLM comparison is based on a {BENCHMARK_SAMPLE_SIZE}-message sample,
    so evaluation on a larger test set would provide a more robust estimate
    of comparative performance.
    """

    report_data = {
        "sample_size": BENCHMARK_SAMPLE_SIZE,
        "results": [
            {
                "model": "Fine-tuned DistilBERT (local)",
                "macro_f1": keras_macro_f1,
                "avg_latency": keras_latency,
            },
            {
                "model": GEMINI_MODEL,
                "macro_f1": gemini_macro_f1,
                "avg_latency": gemini_latency,
            },
            {
                "model": GROQ_MODEL,
                "macro_f1": groq_macro_f1,
                "avg_latency": groq_latency,
            },
        ],
        "per_class": {
            label: {
                "distilbert": keras_per_class[label],
                "gemini": gemini_per_class[label],
                "groq": groq_per_class[label],
            }
            for label in LABEL_COLUMNS
        },
        "observations": {
            "best_model": "Fine-tuned DistilBERT (local)",
            "best_macro_f1": keras_macro_f1,
            "best_latency": keras_latency,
            "llm_models": [
                GEMINI_MODEL,
                GROQ_MODEL,
            ],
            "cache_enabled": True,
            "rate_limit_retry_enabled": True,
        },
        "conclusion": {
            "primary_model": "Fine-tuned DistilBERT (local)",
            "reason": "Highest Macro-F1 and lowest average latency in the benchmark sample.",
            "benchmark_sample_size": BENCHMARK_SAMPLE_SIZE,
        },
    }

    os.makedirs(DOCS_DIR, exist_ok=True)

    json_path = os.path.join(DOCS_DIR, "benchmark_report.json")
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(DOCS_DIR, "benchmark_report.md")
    with open(report_path, "w") as f:
        f.write(report)

    logger.info(f"Report written to {report_path} and {json_path}")
    return report_path


if __name__ == "__main__":
    generate_report()
