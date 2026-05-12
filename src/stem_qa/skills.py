from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cases import Case


Probe = Callable[[object, str], list[str]]


@dataclass(frozen=True)
class Skill:
    name: str
    signal: str
    probe: Probe


def available_skills() -> list[Skill]:
    return [
        Skill("reverse_involution", "reverse", reverse_involution),
        Skill("reverse_changes_text", "reverse", reverse_changes_text),
        Skill("sorted_idempotence", "sorted", sorted_idempotence),
        Skill("sorted_removes_duplicates", "sorted", sorted_removes_duplicates),
        Skill("clamp_bounds", "between min and max", clamp_bounds),
        Skill("slug_shape", "slug", slug_shape),
        Skill("signed_integer_parsing", "integers", signed_integer_parsing),
        Skill("dedupe_preserves_order", "preserving the first occurrence", dedupe_preserves_order),
    ]


def matches(skill: Skill, case: Case) -> bool:
    return skill.signal in case.spec.lower()


def reverse_involution(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    failures = []
    for value in ["abc", "", "racecar", " abc "]:
        if fn(fn(value)) != value:
            failures.append(f"reverse involution failed for {value!r}")
    return failures


def reverse_changes_text(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    result = fn("racecar")
    return ["palindrome did not visibly change"] if result == "racecar" else []


def sorted_idempotence(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    failures = []
    samples = [[3, 1, 2, 1], [], [5, 5, 4]]
    for sample in samples:
        result = fn(sample)
        if result != sorted(sample):
            failures.append(f"sort output mismatch for {sample!r}: {result!r}")
        if fn(result) != result:
            failures.append(f"sort idempotence failed for {sample!r}")
    return failures


def sorted_removes_duplicates(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    result = fn([3, 1, 2, 1])
    return [] if len(result) < 4 else ["duplicates were preserved"]


def clamp_bounds(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    failures = []
    for value, low, high in [(-3, 0, 10), (12, 0, 10), (5, 0, 10)]:
        result = fn(value, low, high)
        if not low <= result <= high:
            failures.append(f"clamp returned {result} outside [{low}, {high}]")
    return failures


def slug_shape(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    failures = []
    result = fn("Hello, JetBrains Intern!")
    if result != result.lower():
        failures.append("slug is not lowercase")
    if " " in result or "," in result or "!" in result:
        failures.append("slug kept separator punctuation")
    return failures


def signed_integer_parsing(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    result = fn("a=-2 b=17 c=0")
    return [] if result == [-2, 17, 0] else [f"integer parse mismatch: {result!r}"]


def dedupe_preserves_order(module: object, function: str) -> list[str]:
    fn = getattr(module, function)
    result = fn(["b", "a", "b", "c", "a"])
    return [] if result == ["b", "a", "c"] else [f"dedupe order mismatch: {result!r}"]
