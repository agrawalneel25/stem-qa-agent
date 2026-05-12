# Submission

## Task #1 - Solution

GitHub repo:

`https://github.com/agrawalneel25/stem-qa-agent`

I built a small stem agent that becomes a Python QA agent. It starts with no active QA skills, reads a set of training specs and target functions, tests candidate QA probes, rejects probes that create false positives, and saves the specialized agent it became.

The repo includes:

- runnable Python code in `src/stem_qa`
- benchmark cases in `benchmark/cases`
- tests in `tests/test_agent.py`
- measured results in `reports/evaluation.md` and `reports/evaluation.json`
- the write-up in `reports/writeup.md`

Current held-out result:

| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic baseline | 0.364 | 0.0 | 0 | 0 | 0 | 7 | 4 |
| Recall-only evolution | 0.818 | 0.857 | 0.857 | 6 | 1 | 1 | 3 |
| Evolved QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |

The useful result is the ablation: recall-only evolution catches the same six held-out bugs but introduces a false positive. The gated stem keeps the same recall and removes the false positive by rejecting a noisy candidate skill during evolution.

Run locally:

```powershell
python -m pip install -e .
python -m unittest discover -s tests
python -m stem_qa --cases benchmark\cases --out reports
python scripts\split_sensitivity.py
```

GitHub Actions runs the tests, benchmark, and split-sensitivity check.

## Task #2 - Solution

My answer is in:

`reports/autonomy_limits.md`

Short version: the blockers are underspecified tasks, long-horizon error compounding, missing social/product context, weak verification for non-testable work, and unsafe tool permissions. I argue for narrower agents with explicit operating envelopes instead of one fully autonomous software engineer.
