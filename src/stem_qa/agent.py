from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .cases import Case, load_cases
from .skills import Skill, available_skills, matches

HAND_BUILT_QA_SKILLS = [
    "reverse_involution",
    "sorted_idempotence",
    "clamp_bounds",
    "slug_shape",
    "signed_integer_parsing",
    "dedupe_preserves_order",
]


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    split: str
    bug_expected: bool
    detected: bool
    findings: list[str]


class StemAgent:
    def __init__(self, skills: list[Skill] | None = None, trace: list[dict[str, object]] | None = None) -> None:
        self.skills = skills or []
        self.trace = trace or []

    @classmethod
    def generic(cls) -> "StemAgent":
        return cls([])

    @classmethod
    def from_skill_names(cls, names: list[str]) -> "StemAgent":
        by_name = {skill.name: skill for skill in available_skills()}
        missing = [name for name in names if name not in by_name]
        if missing:
            raise ValueError(f"unknown skills: {', '.join(missing)}")
        return cls([by_name[name] for name in names])

    def evolve(self, train_cases: list[Case], policy: str = "gated") -> "StemAgent":
        selected: list[Skill] = []
        trace: list[dict[str, object]] = []
        for skill in available_skills():
            relevant = [case for case in train_cases if matches(skill, case)]
            if not relevant:
                continue
            results = [self._run_skill(skill, case) for case in relevant]
            true_hits = sum(1 for case, failures in zip(relevant, results) if case.bug_expected and failures)
            false_hits = sum(1 for case, failures in zip(relevant, results) if not case.bug_expected and failures)
            if policy == "gated":
                accepted = true_hits > 0 and false_hits == 0
            elif policy == "recall_only":
                accepted = true_hits > 0
            else:
                raise ValueError(f"unknown evolution policy: {policy}")
            trace.append(
                {
                    "skill": skill.name,
                    "policy": policy,
                    "matched_training_cases": len(relevant),
                    "true_hits": true_hits,
                    "false_hits": false_hits,
                    "accepted": accepted,
                }
            )
            if accepted:
                selected.append(skill)
        return StemAgent(selected, trace)

    def evaluate(self, cases: list[Case]) -> list[EvaluationResult]:
        return [self._evaluate_one(case) for case in cases]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps({"skills": [skill.name for skill in self.skills], "evolution_trace": self.trace}, indent=2),
            encoding="utf-8",
        )

    def _evaluate_one(self, case: Case) -> EvaluationResult:
        findings: list[str] = []
        for skill in self.skills:
            if matches(skill, case):
                findings.extend(f"{skill.name}: {failure}" for failure in self._run_skill(skill, case))
        return EvaluationResult(case.case_id, case.split, case.bug_expected, bool(findings), findings)

    def _run_skill(self, skill: Skill, case: Case) -> list[str]:
        try:
            module = case.load_module()
            return skill.probe(module, case.function)
        except Exception as exc:
            return [f"{skill.name} crashed: {exc}"]


def summarize(results: list[EvaluationResult]) -> dict[str, float | int]:
    tp = sum(1 for item in results if item.bug_expected and item.detected)
    fp = sum(1 for item in results if not item.bug_expected and item.detected)
    fn = sum(1 for item in results if item.bug_expected and not item.detected)
    tn = sum(1 for item in results if not item.bug_expected and not item.detected)
    total = len(results)
    return {
        "cases": total,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "accuracy": round((tp + tn) / total, 3) if total else 0,
        "recall": round(tp / (tp + fn), 3) if tp + fn else 0,
        "precision": round(tp / (tp + fp), 3) if tp + fp else 0,
    }
