# Bootstrap Intervals

Paired bootstrap over the held-out cases, 2,000 resamples.
The benchmark is small, so the intervals are meant as a warning label rather than a claim of statistical certainty.

| Agent | Accuracy mean | Accuracy 5-95% | Recall mean | Recall 5-95% | Precision mean | Precision 5-95% |
|---|---:|---:|---:|---:|---:|---:|
| Recall-only evolution | 0.818 | 0.636-1.0 | 0.858 | 0.6-1.0 | 0.855 | 0.6-1.0 |
| Hand-built QA agent | 0.91 | 0.727-1.0 | 0.858 | 0.6-1.0 | 1.0 | 1.0-1.0 |
| Evolved QA agent | 0.91 | 0.727-1.0 | 0.858 | 0.6-1.0 | 1.0 | 1.0-1.0 |
