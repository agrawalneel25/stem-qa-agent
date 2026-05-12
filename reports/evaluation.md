# Stem QA Agent Evaluation

Selected skills: reverse_involution, sorted_idempotence, clamp_bounds, slug_shape, signed_integer_parsing, dedupe_preserves_order

| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic baseline | 0.364 | 0.0 | 0 | 0 | 0 | 7 | 4 |
| Recall-only evolution | 0.818 | 0.857 | 0.857 | 6 | 1 | 1 | 3 |
| Hand-built QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |
| Evolved QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |

## Findings

- `07_reverse_clean`: detected=False, expected_bug=False
- `09_clamp_clean`: detected=False, expected_bug=False
- `10_slug_clean`: detected=False, expected_bug=False
- `12_parse_clean`: detected=False, expected_bug=False
- `13_reverse_bug_eval`: detected=True, expected_bug=True
- `14_sort_bug_eval`: detected=True, expected_bug=True
- `15_clamp_bug_eval`: detected=True, expected_bug=True
- `16_slug_bug_eval`: detected=True, expected_bug=True
- `17_dedupe_bug_eval`: detected=True, expected_bug=True
- `18_parse_bug_eval`: detected=True, expected_bug=True
- `19_median_bug_eval`: detected=False, expected_bug=True

## Evolution Trace

- `reverse_involution`: accepted=True, true_hits=1, false_hits=0
- `reverse_changes_text`: accepted=False, true_hits=1, false_hits=1
- `sorted_idempotence`: accepted=True, true_hits=1, false_hits=0
- `sorted_removes_duplicates`: accepted=False, true_hits=0, false_hits=1
- `clamp_bounds`: accepted=True, true_hits=1, false_hits=0
- `slug_shape`: accepted=True, true_hits=1, false_hits=0
- `signed_integer_parsing`: accepted=True, true_hits=1, false_hits=0
- `dedupe_preserves_order`: accepted=True, true_hits=1, false_hits=0
