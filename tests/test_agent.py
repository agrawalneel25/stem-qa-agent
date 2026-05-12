import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stem_qa import StemAgent, load_cases
from stem_qa.agent import summarize


ROOT = Path(__file__).resolve().parents[1]


class StemAgentTest(unittest.TestCase):
    def test_evolution_improves_held_out_recall(self) -> None:
        cases = load_cases(ROOT / "benchmark/cases")
        train = [case for case in cases if case.split == "train"]
        test = [case for case in cases if case.split == "test"]

        baseline = StemAgent.generic()
        evolved = baseline.evolve(train)
        recall_only = baseline.evolve(train, policy="recall_only")

        baseline_summary = summarize(baseline.evaluate(test))
        evolved_summary = summarize(evolved.evaluate(test))
        recall_only_summary = summarize(recall_only.evaluate(test))

        self.assertEqual(baseline_summary["recall"], 0.0)
        self.assertGreater(evolved_summary["recall"], baseline_summary["recall"])
        self.assertEqual(evolved_summary["false_positive"], 0)
        self.assertGreater(recall_only_summary["false_positive"], evolved_summary["false_positive"])
        self.assertTrue(any(step["accepted"] for step in evolved.trace))
        self.assertTrue(any(not step["accepted"] for step in evolved.trace))
        self.assertIn("median", [case.case_id.split("_")[1] for case in test if case.bug_expected])

    def test_cli_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "stem_qa",
                    "--cases",
                    str(ROOT / "benchmark/cases"),
                    "--out",
                    directory,
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            payload = json.loads((Path(directory) / "evaluation.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["evolved"]["true_positive"], 6)
            self.assertEqual(payload["evolved"]["false_negative"], 1)
            self.assertIn("recall_only", payload)
            self.assertTrue((Path(directory) / "evaluation.md").exists())


if __name__ == "__main__":
    unittest.main()
