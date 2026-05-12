# Split Sensitivity

Ten stratified train/test splits. Each split trains on 8 buggy and 4 clean cases, then tests on the rest.

| Seed | Gated recall | Gated FP | Recall-only recall | Recall-only FP | Accepted skills |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.6 | 0 | 0.6 | 1 | 5 |
| 1 | 0.8 | 0 | 0.8 | 1 | 6 |
| 2 | 0.8 | 0 | 0.8 | 1 | 6 |
| 3 | 0.4 | 0 | 0.4 | 0 | 5 |
| 4 | 0.4 | 0 | 0.4 | 1 | 5 |
| 5 | 0.4 | 0 | 0.4 | 1 | 5 |
| 6 | 1.0 | 0 | 1.0 | 1 | 6 |
| 7 | 0.8 | 0 | 0.8 | 1 | 6 |
| 8 | 1.0 | 0 | 1.0 | 1 | 6 |
| 9 | 0.4 | 0 | 0.4 | 1 | 5 |

Mean gated recall: 0.660
Mean gated false positives: 0.000
Mean recall-only false positives: 0.900
