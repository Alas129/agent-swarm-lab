# The agent loop (ReAct)

> **Level 1 · Lab 02** — Turn a one-shot LLM call into an agent by interleaving
> **rea**soning and **act**ing in a loop. Build the ReAct loop and its parser from scratch.

## Prerequisites

- [Lab 01 — LLM as reasoner](../01-llm-as-reasoner/README.md).

## Learning objectives

After this lab you can:

- Explain the **ReAct** pattern: Thought → Action → Observation, repeated.
- Implement the loop yourself: prompt format, output parsing, stop sequences, and a step limit.
- Say why the loop (not the model) is what makes something an "agent."

## Concept

A single call can reason *or* produce an answer, but it can't check its work against the
world. **ReAct** (Yao et al., 2022) fixes this by having the model emit interleaved
reasoning traces and actions, then feeding the action's result back in:

```
            ┌───────────────────────────────────────────────┐
 Question ─►│  Thought:  reason about what to do next        │
            │  Action:   pick a tool                         │◄── loop until
            │  Action Input: the argument                    │    "Final Answer"
            │  Observation: ← tool result is fed back in     │
            └───────────────────────────────────────────────┘
                                  │ Final Answer
                                  ▼
                               Answer
```

Reasoning helps the model plan and track what it's doing; actions let it pull in new
information it didn't have. The two together beat either alone.

### How we implement it from scratch

1. A **system prompt** tells the model to respond in a strict `Thought / Action /
   Action Input` format, and to emit `Final Answer:` when done.
2. We call the model with a **stop sequence** (`"Observation:"`) so it stops and hands
   control back to *us* to run the tool — the model never hallucinates its own observations.
3. We **parse** the output, run the chosen tool, and append `Observation: <result>` to a
   running **scratchpad** that we resend each step.
4. A **step limit** prevents infinite loops.

This lab uses a single tool — a calculator — so we can focus on the *loop*. Lab 03
generalizes to many tools.

## In this lab

`lab.py` implements `safe_calc` (a sandboxed arithmetic evaluator), `parse_react_output`
(the parser), and `run_agent` (the loop), then solves a multi-step word problem so you can
watch the THOUGHT / ACTION / OBSERVATION trace.

```bash
uv run python levels/01-foundations/02-the-agent-loop/lab.py
```

## Under the hood (no magic)

This lab uses two `shared/` helpers. Neither is doing anything you couldn't inline:

- **`Tracer`** ([`shared/tracing.py`](../../../shared/tracing.py)) is just labelled prints:
  ```python
  def thought(s):      print(f"[THOUGHT] {s}")
  def action(t, i):    print(f"[ACTION] {t}({i})")
  def observation(s):  print(f"[OBSERVATION] {s}")
  ```
- **`llm.complete(..., stop=["Observation:"])`** is the [Lab 01](../01-llm-as-reasoner/README.md#under-the-hood-no-magic)
  Anthropic call with one extra argument — the stop sequence that hands control back to us:
  ```python
  response = client.messages.create(
      model="claude-sonnet-4-6", max_tokens=1024, temperature=0.0,
      system=SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}],
      stop_sequences=["Observation:"],   # <-- stop before the model invents a result
  )
  ```

The *loop, parser, and scratchpad* — the actual agent — are written from scratch right
here in `lab.py`. `shared/` only saves you the boilerplate around them.

## Try it

See [exercises.md](exercises.md).

## Sources

- [Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)](https://arxiv.org/abs/2210.03629)
  — the reasoning-and-acting loop this lab implements.
- [Anthropic, "Building effective agents" — Agents](https://www.anthropic.com/engineering/building-effective-agents)
  — agents as an LLM running tools in a loop, with stopping conditions.
