# Planning & reflection

> **Level 2 · Lab 02** — Two reasoning strategies that make agents more reliable:
> **plan-and-execute** (decompose first) and **reflexion** (self-critique and retry).

## Prerequisites

- [Level 1 — Foundations](../../01-foundations/README.md).
- [Lab 2.01 — Structured output](../01-structured-output/README.md) helps but isn't required.

## Learning objectives

After this lab you can:

- Implement **plan-and-execute**: have the model produce a plan, then carry out each step
  with the results of earlier steps in context.
- Implement **reflexion**: generate an answer, critique it, and retry using the critique as
  a "lesson," until it passes or you hit a limit.
- Reason about *when* each helps — and the cost (more LLM calls) they add.

## Concept

A single LLM call answers in one shot. For harder tasks, two structures help:

**Plan-and-execute** — think before doing. The model first writes a plan; then each step
runs with the previous steps' results available. This keeps long tasks on track.

```
 task ─► [plan] ─► [step 1] ─► [step 2] ─► ... ─► [synthesize] ─► answer
                      └── each step sees earlier results ──┘
```

**Reflexion** — learn from your own mistakes within a task. Produce an attempt, critique
it, and if it's not good enough, retry with the critique fed back as a lesson.

```
        ┌──────────────────────────────────────────────┐
 task ─►│ attempt ─► critique ─► PASS? ── no ──► retry  │◄─┐
        │                          │ (lesson fed back)   │ │
        └──────────────────────────┼─────────────────────┘ │
                                   yes                       │ until PASS
                                    ▼                        │ or max_iters
                                 answer ──────────────────────┘
```

Both trade extra LLM calls (cost, latency) for reliability. Use them when one shot isn't
enough — not by default.

## In this lab

`lab.py` implements `make_plan` / `execute_plan` (plan-and-execute) and `reflexion`
(critique-and-retry), plus the parsers they need. Run it:

```bash
uv run python levels/02-tools-memory-reasoning/02-planning-and-reflection/lab.py
```

## Under the hood (no magic)

Only `LLMClient`/`Tracer` come from `shared/`. Both strategies are just orchestration of
plain `llm.complete(...)` calls around small parsers — there's no planner library:

```python
plan  = parse_plan(llm.complete("Break this task into numbered steps: ..."))
# ...run each step...
verdict = llm.complete("Critique this answer; end with VERDICT: PASS or VERDICT: FAIL")
```

## Try it

See [exercises.md](exercises.md).

## Sources

- [Wang et al., "Plan-and-Solve Prompting" (2023)](https://arxiv.org/abs/2305.04091)
  — plan first, then execute, to improve multi-step reasoning.
- [Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023)](https://arxiv.org/abs/2303.11366)
  — agents that verbally reflect on failures and retry.
- [Yao et al., "Tree of Thoughts" (2023)](https://arxiv.org/abs/2305.10601)
  — deliberate search over reasoning steps (a richer cousin of these patterns).
