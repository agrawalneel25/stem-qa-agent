# Evolution Lineage

The stem starts with no active probes. Each candidate is tested on the training environment.
A candidate survives only when it catches at least one known bug and does not flag clean training cases.

| Candidate skill | Matched training cases | True hits | False hits | Decision |
|---|---:|---:|---:|---|
| `reverse_involution` | 2 | 1 | 0 | kept |
| `reverse_changes_text` | 2 | 1 | 1 | rejected |
| `sorted_idempotence` | 2 | 1 | 0 | kept |
| `sorted_removes_duplicates` | 2 | 0 | 1 | rejected |
| `clamp_bounds` | 1 | 1 | 0 | kept |
| `slug_shape` | 1 | 1 | 0 | kept |
| `signed_integer_parsing` | 1 | 1 | 0 | kept |
| `dedupe_preserves_order` | 2 | 1 | 0 | kept |

The hand-built QA baseline uses the same non-noisy probe set that a person would probably select after reading the specs.
The evolved agent reaches the same held-out score without being told that set directly.
