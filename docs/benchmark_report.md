# LLM Benchmark Report

Sample size: 100 messages from held-out Jigsaw test set.

Both LLM services used are free-tier — cost is not applicable/tracked, but
free-tier requests are subject to rate limits which real deployments would
need to work around.

## Results

| Model | Macro-F1 | Avg Latency (s) |
|---|---:|---:|
| **Fine-tuned DistilBERT (local)** | **0.5973** | **0.1807** |
| Gemini 2.5 Flash | 0.0370 | 0.2774 |
| Qwen/Qwen3.6-27B | 0.2343 | 1.5511 |

## Per-Class F1

| Category | DistilBERT | Gemini | Qwen/Qwen3.6-27B |
|---|---:|---:|---:|
| toxic | **0.673** | 0.222 | 0.462 |
| severe_toxic | **0.358** | 0.000 | 0.000 |
| obscene | **0.700** | 0.000 | 0.444 |
| threat | **0.526** | 0.000 | 0.000 |
| insult | **0.693** | 0.000 | 0.500 |
| identity_hate | **0.634** | 0.000 | 0.000 |

## Observations

The fine-tuned DistilBERT model achieved the highest Macro-F1 at 0.5973,
outperforming both Qwen/Qwen3.6-27B at 0.2343 and Gemini 2.5 Flash at
0.0370.

DistilBERT also achieved the lowest average latency at 0.1807 seconds per
message. Gemini 2.5 Flash had an average latency of 0.2774 seconds, while
Qwen/Qwen3.6-27B had the highest latency at 1.5511 seconds.

At the per-class level, DistilBERT achieved its strongest F1 scores on
obscene (0.700), insult (0.693), and toxic (0.673). It also produced
non-zero F1 scores across all six toxicity categories, whereas the tested
LLM classifiers produced zero F1 for several categories in this sample.

All LLM results were cached per input. This allows previously classified
messages to be skipped when the benchmark is re-run after an interruption
or rate-limit event.

Since both LLM options were accessed through free-tier services, API cost
was not tracked in this benchmark. The comparison therefore focuses on
classification performance and inference latency.

## Conclusion

The benchmark shows that the fine-tuned local DistilBERT model provided
the strongest overall performance among the three evaluated approaches.

It achieved a Macro-F1 of 0.5973 while also providing the lowest measured
latency of 0.1807 seconds per message. The results support using the
fine-tuned DistilBERT model as the primary toxicity classification model,
while the LLM-based approaches can be considered alternative or
supplementary classifiers.

The LLM comparison is based on a 100-message sample, so larger-scale
evaluation would provide a more robust estimate of comparative performance.