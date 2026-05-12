# Stem QA Agent

This is my solution for the JetBrains AI Engineering Intern task. I chose a narrow domain: a stem agent that becomes a Python QA agent for small utility functions.

The stem starts with no QA skills. It reads training examples, tries candidate probes, keeps the probes that find real bugs without false positives, and then evaluates the specialized agent on held-out cases.

## Run

```powershell
python -m pip install -e .
python -m unittest discover -s tests
python -m stem_qa --cases benchmark\cases --out reports
python scripts\split_sensitivity.py
python scripts\bootstrap_ci.py
```

On Linux/macOS:

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m stem_qa --cases benchmark/cases --out reports
python scripts/split_sensitivity.py
python scripts/bootstrap_ci.py
```

## Result

Current held-out evaluation:

| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic baseline | 0.364 | 0.0 | 0 | 0 | 0 | 7 | 4 |
| Recall-only evolution | 0.818 | 0.857 | 0.857 | 6 | 1 | 1 | 3 |
| Hand-built QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |
| Evolved QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |

Generated files:

- `reports/evaluation.md`
- `reports/evaluation.json`
- `reports/lineage.md`
- `reports/split_sensitivity.md`
- `reports/bootstrap_ci.md`
- `reports/specialized_agent.json`

## How It Maps To The Prompt

- **Stem agent**: `StemAgent.generic()` starts with no selected QA probes.
- **Signals from environment**: training specs and target functions under `benchmark/cases`.
- **Transformation**: `evolve()` selects a task-specific skill set.
- **Safeguard**: a skill is kept only if it catches at least one training bug and causes no training false positives.
- **Stop condition**: stop when no more candidate skills pass that gate.
- **Execution**: the specialized QA agent runs only the selected skills on held-out tasks.

## Files

- `src/stem_qa/agent.py` - evolution and evaluation loop
- `src/stem_qa/skills.py` - candidate QA skills
- `benchmark/cases/` - train/test benchmark cases
- `tests/test_agent.py` - regression tests
- `reports/writeup.md` - main write-up
- `reports/autonomy_limits.md` - answer to Task 2
- `DESIGN.md` - design choices and limits

The recall-only row is the useful comparison. It selects any skill that catches a training bug, even if it also flags clean examples. The gated stem keeps the same held-out recall but removes the false positive by rejecting noisy candidate skills during evolution.

The hand-built row is a sanity check. It uses the non-noisy probes I would have selected manually after reading the benchmark. The evolved stem reaches the same held-out score from the training gate alone.
