from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
from types import ModuleType


@dataclass(frozen=True)
class Case:
    case_id: str
    split: str
    function: str
    bug_expected: bool
    path: Path
    spec: str

    def load_module(self) -> ModuleType:
        spec = importlib.util.spec_from_file_location(f"case_{self.case_id}", self.path / "target.py")
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {self.path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def load_cases(root: str | Path) -> list[Case]:
    root = Path(root)
    cases: list[Case] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
        cases.append(
            Case(
                case_id=path.name,
                split=meta["split"],
                function=meta["function"],
                bug_expected=bool(meta["bug_expected"]),
                path=path,
                spec=(path / "spec.txt").read_text(encoding="utf-8"),
            )
        )
    return cases

