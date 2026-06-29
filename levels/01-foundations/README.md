# Level 1 — Foundations (single agent)

Build a real agent from scratch, one concept at a time. By the end of this level you'll
have written — without any agent framework — the exact machinery that LangGraph, CrewAI,
and the others provide for you: a reasoning loop, tool calling, and memory.

## Prerequisites

- [Level 0 — Orientation](../00-orientation/README.md) completed; `hello.py` runs.
- Comfortable reading Python. No prior agent experience needed.

## The labs (do them in order)

1. **[01 — LLM as reasoner](01-llm-as-reasoner/README.md)** — the model is a stateless
   next-token predictor. Prompting, system prompts, temperature, and (non-)determinism.
2. **[02 — The agent loop (ReAct)](02-the-agent-loop/README.md)** — interleave reasoning
   and acting in a loop. Build the ReAct loop and its output parser from scratch.
3. **[03 — Tool calling](03-tool-calling/README.md)** — give the agent tools. A `Tool`
   abstraction, a registry, dispatch, and error handling, built from scratch.
4. **[04 — Basic memory](04-basic-memory/README.md)** — agents are stateless between
   calls. Build conversation memory and respect the context window.

## How to run

```bash
# run a lab
uv run python levels/01-foundations/02-the-agent-loop/lab.py

# run all Level 1 tests (these pass offline — no API key needed)
uv run pytest levels/01-foundations
```

The labs need an `ANTHROPIC_API_KEY` to call the model, but every `lab.py` degrades
gracefully without one. The tests never call the network — they inject a scripted fake
LLM (`shared/testing.py`).

## What you'll have built

A small, framework-free agent that reasons in a loop, calls tools you define, handles
tool errors, and remembers a conversation — the foundation every later level extends.
