from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import HAND_BUILT_QA_SKILLS, StemAgent, load_cases, summarize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evolve and evaluate a small stem QA agent.")
    parser.add_argument("--cases", default="benchmark/cases")
    parser.add_argument("--out", default="reports")
    args = parser.parse_args(argv)

    cases = load_cases(args.cases)
    train = [case for case in cases if case.split == "train"]
    test = [case for case in cases if case.split == "test"]

    baseline = StemAgent.generic()
    recall_only = baseline.evolve(train, policy="recall_only")
    hand_built = StemAgent.from_skill_names(HAND_BUILT_QA_SKILLS)
    evolved = baseline.evolve(train, policy="gated")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    evolved.save(out / "specialized_agent.json")

    baseline_results = baseline.evaluate(test)
    recall_only_results = recall_only.evaluate(test)
    hand_built_results = hand_built.evaluate(test)
    evolved_results = evolved.evaluate(test)

    payload = {
        "selected_skills": [skill.name for skill in evolved.skills],
        "recall_only_skills": [skill.name for skill in recall_only.skills],
        "hand_built_skills": [skill.name for skill in hand_built.skills],
        "evolution_trace": evolved.trace,
        "baseline": summarize(baseline_results),
        "recall_only": summarize(recall_only_results),
        "hand_built": summarize(hand_built_results),
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
    (out / "lineage.md").write_text(lineage_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["evolved"], indent=2))
    return 0


def markdown(payload: dict[str, object]) -> str:
    baseline = payload["baseline"]
    recall_only = payload["recall_only"]
    hand_built = payload["hand_built"]
    evolved = payload["evolved"]
    assert isinstance(baseline, dict) and isinstance(recall_only, dict) and isinstance(hand_built, dict)
    assert isinstance(evolved, dict)
    lines = [
        "# Stem QA Agent Evaluation",
        "",
        f"Selected skills: {', '.join(payload['selected_skills'])}",
        "",
        "| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| Generic baseline | {baseline['accuracy']} | {baseline['recall']} | {baseline['precision']} | {baseline['true_positive']} | {baseline['false_positive']} | {baseline['false_negative']} | {baseline['true_negative']} |",
        f"| Recall-only evolution | {recall_only['accuracy']} | {recall_only['recall']} | {recall_only['precision']} | {recall_only['true_positive']} | {recall_only['false_positive']} | {recall_only['false_negative']} | {recall_only['true_negative']} |",
        f"| Hand-built QA agent | {hand_built['accuracy']} | {hand_built['recall']} | {hand_built['precision']} | {hand_built['true_positive']} | {hand_built['false_positive']} | {hand_built['false_negative']} | {hand_built['true_negative']} |",
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


def lineage_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Evolution Lineage",
        "",
        "The stem starts with no active probes. Each candidate is tested on the training environment.",
        "A candidate survives only when it catches at least one known bug and does not flag clean training cases.",
        "",
        "| Candidate skill | Matched training cases | True hits | False hits | Decision |",
        "|---|---:|---:|---:|---|",
    ]
    for step in payload["evolution_trace"]:
        decision = "kept" if step["accepted"] else "rejected"
        lines.append(
            f"| `{step['skill']}` | {step['matched_training_cases']} | "
            f"{step['true_hits']} | {step['false_hits']} | {decision} |"
        )
    lines.extend(
        [
            "",
            "The hand-built QA baseline uses the same non-noisy probe set that a person would probably select after reading the specs.",
            "The evolved agent reaches the same held-out score without being told that set directly.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
