# Stem QA Agent Write-up

## What I Built

I interpreted "stem agent" as an agent that does not start with a fixed task harness. It starts with candidate behaviors, reads a small environment, keeps the behaviors that help, rejects the ones that look unsafe, and then executes as a specialized agent.

I chose quality assurance for small Python utility functions because the feedback loop is measurable. A QA agent either catches a seeded defect or it does not. The benchmark is small, but it lets the agent show the core stem-cell pattern: generic state, environmental signals, specialization, safeguard, and execution.

The stem agent begins with no active QA probes. It reads training cases under `benchmark/cases`, each with a short natural-language spec and a target Python function. Candidate skills look for signals such as "reverse", "sorted", "between min and max", "slug", "integers", and "preserving the first occurrence". A skill survives only when it catches at least one training bug and causes no false positives on the training split. That is the safeguard: a mutation that helps but breaks clean examples is pulled back.

## Architecture

The code is deliberately small:

- `StemAgent.generic()` creates an agent with no selected skills.
- `evolve(train_cases)` evaluates candidate QA probes against the training split.
- `evaluate(test_cases)` runs the selected skills on held-out examples.
- `reports/specialized_agent.json` records what the agent became and why each candidate skill was kept or rejected.

The selected QA skills are not meant to be universal. They are the agent's phenotype for this task class. For another task class, the stem would be rerun with a different environment and different candidate behaviors.

## Experiment

The benchmark has train and held-out test cases. Bugs include whitespace loss in reverse, duplicate loss in sorting, incorrect clamp upper bound, incomplete slugification, missing signed integer parsing, and order loss in deduplication. I added one held-out median bug that the skill library does not cover. That case is useful because it prevents a perfect-score demo and shows the boundary of the approach.

Current held-out result:

| Agent | Accuracy | Recall | Precision | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic baseline | 0.364 | 0.0 | 0 | 0 | 0 | 7 | 4 |
| Evolved QA agent | 0.909 | 0.857 | 1.0 | 6 | 0 | 1 | 4 |

The generic baseline has no active probes, so it only represents "do nothing beyond loading the task class". The evolved agent selected six probes and found six of seven held-out bugs with no false positives. The missed case was `19_median_bug_eval`, where the spec says even-length lists should average the two middle values. The stem had no candidate median skill, so it could not become that kind of checker.

## What Surprised Me

The strongest part of the design was not the probe library. It was the rollback rule. Without the false-positive gate, it is easy to select broad probes that look useful on buggy examples but are noisy on clean ones. The small training clean set matters because it teaches the agent what not to become.

The main failure was coverage. The stem can only specialize into shapes available in its candidate pool. It can select, reject, and compose skills, but it cannot invent a median oracle from nothing. In a larger version, I would add an LLM-backed skill proposal step, then require the same empirical gate before accepting generated probes.

## What I Would Do Next

I would extend this in three directions:

1. Use an LLM to propose candidate probes from specs, but keep acceptance deterministic and test-based.
2. Add a patching phase after detection, with rollback if tests or probes regress.
3. Run on real small Python packages, not only synthetic utilities.

The lesson is that "self-building" should not mean uncontrolled rewriting. The stem agent needs a narrow environment, a candidate behavior space, measurable feedback, and a way to reject unsafe specialization.
