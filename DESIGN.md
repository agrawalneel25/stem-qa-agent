# Design Notes

## Domain Choice

I chose QA for small Python functions because it gives a cheap feedback loop. The agent can run probes, get binary evidence, and compare against held-out labels. That is narrower than a full coding agent, but the prompt says the result does not need to be universal.

## Stem Mechanism

The stem agent starts with no active QA skills. It has a pool of candidate probes in `src/stem_qa/skills.py`. Each probe has:

- a signal it looks for in the task spec
- a concrete test it can run against the target function
- a failure message if the target breaks the expected property

`StemAgent.evolve()` is the transformation step. It runs each candidate on training cases whose specs match the signal. Under the default `gated` policy, the agent keeps a candidate only when it catches at least one training bug and causes no training false positives.

## Why The Ablation Matters

I added `recall_only` as a weaker evolution policy. It accepts any candidate that catches a training bug. That sounds reasonable if the only goal is recall, but it selected a noisy reverse probe and caused one held-out false positive.

Current held-out result:

| Agent | Accuracy | Recall | Precision | FP |
|---|---:|---:|---:|---:|
| Generic baseline | 0.364 | 0.0 | 0 | 0 |
| Recall-only evolution | 0.818 | 0.857 | 0.857 | 1 |
| Hand-built QA agent | 0.909 | 0.857 | 1.0 | 0 |
| Gated evolution | 0.909 | 0.857 | 1.0 | 0 |

The gated version did not catch more bugs. It became safer at the same recall.

I also added a hand-built QA baseline. It uses the non-noisy probes a person would probably choose after reading the specs. The gated stem reaches the same held-out score through the training gate, which is the basic evidence that it became the intended specialist rather than only beating a weak baseline.

## What This Is Not

This is not a claim that a few handwritten probes are enough for real QA. The useful part is the control loop:

1. propose candidate behavior
2. bind it to task signals
3. test it against training examples
4. reject behavior that creates false positives
5. save the specialized agent and run it on held-out tasks

The next version would use a language model to propose candidate probes from specs, but still require the same empirical gate before accepting them.
