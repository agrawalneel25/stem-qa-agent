from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stem_qa import StemAgent, load_cases  # noqa: E402
from stem_qa.agent import HAND_BUILT_QA_SKILLS, EvaluationResult, summarize  # noqa: E402


def main() -> int:
    cases = load_cases(ROOT / "benchmark/cases")
    train = [case for case in cases if case.split == "train"]
    test = [case for case in cases if case.split == "test"]

    baseline = StemAgent.generic()
    agents = {
        "recall_only": baseline.evolve(train, policy="recall_only"),
        "hand_built": StemAgent.from_skill_names(HAND_BUILT_QA_SKILLS),
        "evolved": baseline.evolve(train, policy="gated"),
    }

    rows = {
        name: bootstrap(agent.evaluate(test), iterations=2000, seed=17)
        for name, agent in agents.items()
    }

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "bootstrap_ci.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (out / "bootstrap_ci.md").write_text(markdown(rows), encoding="utf-8")
    print(markdown(rows))
    return 0


def bootstrap(results: list[EvaluationResult], iterations: int, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    samples = {"accuracy": [], "recall": [], "precision": []}
    for _ in range(iterations):
        draw = [rng.choice(results) for _ in results]
        summary = summarize(draw)
        for metric in samples:
            samples[metric].append(float(summary[metric]))
    return {
        metric: {
            "mean": round(sum(values) / len(values), 3),
            "p05": percentile(values, 0.05),
            "p95": percentile(values, 0.95),
        }
        for metric, values in samples.items()
    }


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * q)
    return round(ordered[index], 3)


def markdown(rows: dict[str, object]) -> str:
    lines = [
        "# Bootstrap Intervals",
        "",
        "Paired bootstrap over the held-out cases, 2,000 resamples.",
        "The benchmark is small, so the intervals are meant as a warning label rather than a claim of statistical certainty.",
        "",
        "| Agent | Accuracy mean | Accuracy 5-95% | Recall mean | Recall 5-95% | Precision mean | Precision 5-95% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "recall_only": "Recall-only evolution",
        "hand_built": "Hand-built QA agent",
        "evolved": "Evolved QA agent",
    }
    for key, label in labels.items():
        row = rows[key]
        assert isinstance(row, dict)
        accuracy = row["accuracy"]
        recall = row["recall"]
        precision = row["precision"]
        assert isinstance(accuracy, dict) and isinstance(recall, dict) and isinstance(precision, dict)
        lines.append(
            f"| {label} | {accuracy['mean']} | {accuracy['p05']}-{accuracy['p95']} | "
            f"{recall['mean']} | {recall['p05']}-{recall['p95']} | "
            f"{precision['mean']} | {precision['p05']}-{precision['p95']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
