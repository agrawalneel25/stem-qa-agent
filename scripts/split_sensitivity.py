from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stem_qa import StemAgent, load_cases  # noqa: E402
from stem_qa.agent import summarize  # noqa: E402


def main() -> int:
    cases = load_cases(ROOT / "benchmark/cases")
    bugs = [case for case in cases if case.bug_expected]
    clean = [case for case in cases if not case.bug_expected]
    rows = []
    for seed in range(10):
        rng = random.Random(seed)
        train_bugs = rng.sample(bugs, 8)
        train_clean = rng.sample(clean, 4)
        train_ids = {case.case_id for case in train_bugs + train_clean}
        train = [case for case in cases if case.case_id in train_ids]
        test = [case for case in cases if case.case_id not in train_ids]

        baseline = StemAgent.generic()
        recall_only = baseline.evolve(train, policy="recall_only")
        gated = baseline.evolve(train, policy="gated")
        rows.append(
            {
                "seed": seed,
                "train_cases": len(train),
                "test_cases": len(test),
                "recall_only": summarize(recall_only.evaluate(test)),
                "gated": summarize(gated.evaluate(test)),
                "accepted_skills": [skill.name for skill in gated.skills],
            }
        )

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "split_sensitivity.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (out / "split_sensitivity.md").write_text(markdown(rows), encoding="utf-8")
    print(markdown(rows))
    return 0


def markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Split Sensitivity",
        "",
        "Ten stratified train/test splits. Each split trains on 8 buggy and 4 clean cases, then tests on the rest.",
        "",
        "| Seed | Gated recall | Gated FP | Recall-only recall | Recall-only FP | Accepted skills |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    gated_recalls = []
    gated_fps = []
    recall_only_fps = []
    for row in rows:
        gated = row["gated"]
        recall_only = row["recall_only"]
        assert isinstance(gated, dict) and isinstance(recall_only, dict)
        gated_recalls.append(float(gated["recall"]))
        gated_fps.append(int(gated["false_positive"]))
        recall_only_fps.append(int(recall_only["false_positive"]))
        lines.append(
            f"| {row['seed']} | {gated['recall']} | {gated['false_positive']} | "
            f"{recall_only['recall']} | {recall_only['false_positive']} | {len(row['accepted_skills'])} |"
        )
    lines.extend(
        [
            "",
            f"Mean gated recall: {sum(gated_recalls) / len(gated_recalls):.3f}",
            f"Mean gated false positives: {sum(gated_fps) / len(gated_fps):.3f}",
            f"Mean recall-only false positives: {sum(recall_only_fps) / len(recall_only_fps):.3f}",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
