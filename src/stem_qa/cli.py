from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import StemAgent, load_cases, summarize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evolve and evaluate a small stem QA agent.")
    parser.add_argument("--cases", default="benchmark/cases")
    parser.add_argument("--out", default="reports")
    args = parser.parse_args(argv)

    cases = load_cases(args.cases)
    train = [case for case in cases if case.split == "train"]
    test = [case for case in cases if case.split == "test"]

    baseline = StemAgent.generic()
    evolved = baseline.evolve(train)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    evolved.save(out / "specialized_agent.json")

    baseline_results = baseline.evaluate(test)
    evolved_results = evolved.evaluate(test)

    payload = {
        "selected_skills": [skill.name for skill in evolved.skills],
        "evolution_trace": evolved.trace,
        "baseline": summarize(baseline_results),
        "evolved": summarize(evolved_results),
        "cases": [
            {
                "case_id": item.case_id,
                "bug_expected": item.bug_expected,
                "detected": item.detected,
                "findings": item.findings,
            }
            for item in evolved_results
        ],
    }
    (out / "evaluation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out / "evaluation.md").write_text(markdown(payload), encoding="utf-8")
    print(json.dumps(payload["evolved"], indent=2))
    return 0


def markdown(payload: dict[str, object]) -> str:
    baseline = payload["baseline"]
    evolved = payload["evolved"]
    assert isinstance(baseline, dict) and isinstance(evolved, dict)
    lines = [
        "# Stem QA Agent Evaluation",
        "",
        f"Selected skills: {', '.join(payload['selected_skills'])}",
        "",
        "| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| Generic baseline | {baseline['accuracy']} | {baseline['recall']} | {baseline['precision']} | {baseline['true_positive']} | {baseline['false_positive']} | {baseline['false_negative']} | {baseline['true_negative']} |",
        f"| Evolved QA agent | {evolved['accuracy']} | {evolved['recall']} | {evolved['precision']} | {evolved['true_positive']} | {evolved['false_positive']} | {evolved['false_negative']} | {evolved['true_negative']} |",
        "",
        "## Findings",
        "",
    ]
    for case in payload["cases"]:
        lines.append(f"- `{case['case_id']}`: detected={case['detected']}, expected_bug={case['bug_expected']}")
    lines.extend(["", "## Evolution Trace", ""])
    for step in payload["evolution_trace"]:
        lines.append(
            f"- `{step['skill']}`: accepted={step['accepted']}, "
            f"true_hits={step['true_hits']}, false_hits={step['false_hits']}"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
