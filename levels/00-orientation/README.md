# Level 0 — Orientation & Setup

> Get the vocabulary straight and confirm your environment works, before you write a
> single agent.

## Learning objectives

After this level you can:

- Explain what an **agent** is and how it differs from a **workflow**.
- Describe the **agent loop** at an intuitive level.
- Find your way around this repo.
- Run a "hello, LLM" check that confirms your API key and dependencies work.

## Agent vs. workflow — the distinction that matters

People say "AI agent" for a lot of different systems. Anthropic draws a useful line that
we'll use throughout this curriculum:

- **Workflows** are systems where LLMs and tools are orchestrated through **predefined
  code paths**. *You* wrote the flow chart; the LLM fills in steps.
- **Agents** are systems where the LLM **dynamically directs its own process and tool
  usage**, deciding what to do next in a loop. The control flow is decided at runtime by
  the model, not hard-coded by you.

Neither is "better." Workflows give you predictability and are often the right choice.
Agents trade predictability for flexibility on open-ended tasks. A recurring theme of
this lab: **start simple, and only add agency (and extra agents) when the task actually
needs it.**

```
Workflow:   input ──► step A ──► step B ──► step C ──► output
                      (you decide the path in advance)

Agent:      input ──►  ┌──────────────────────────────┐
                       │  LLM decides next action      │ ◄─┐
                       │  → act → observe result       │   │  loop until
                       └──────────────────────────────┘ ──┘  done
                      (the model decides the path at runtime)
```

That loop on the right — decide, act, observe, repeat — is the **agent loop**. It's the
heart of everything that follows. You'll build it from scratch in
[Level 1, Lab 02](../01-foundations/02-the-agent-loop/README.md).

## Repo tour

```
shared/      reusable utilities every lab builds on
  llm.py       a tiny provider-agnostic LLM client (Anthropic by default)
  tracing.py   a tracer that prints an agent's THOUGHT / ACTION / OBSERVATION steps
concepts/    the language-agnostic concept index + glossary
levels/      the curriculum (you are here)
ROADMAP.md   the full plan and build status
```

Read [`concepts/glossary.md`](../../concepts/glossary.md) now — even skimming the terms
(agent, workflow, agent loop, ReAct, tool use, token, context window) will make the
foundations labs click faster.

## Hello, LLM — confirm your environment

First, make sure setup is done (see the [root README](../../README.md)):

```bash
uv sync --extra dev          # install deps
cp .env.example .env         # then paste your ANTHROPIC_API_KEY into .env
```

Then run the check:

```bash
uv run python levels/00-orientation/hello.py
```

You should see a one-line greeting from the model. If your key isn't set, the script
prints setup instructions instead of crashing — that graceful-degradation pattern is how
every lab in this repo behaves. The whole thing is just a single LLM call:

```python
from shared import LLMClient

llm = LLMClient()
reply = llm.complete([{"role": "user", "content": "Reply with a friendly one-line hello."}])
print(reply)
```

That single call is also the entire "building block" agents are made of — Anthropic calls
it the *augmented LLM*. Everything else in this curriculum is structure built around
calls like this one.

## Next

→ [Level 1 — Foundations](../01-foundations/README.md): build a real agent from this
single call, one concept at a time.

## Sources

- [Anthropic, "Building effective agents" (Dec 2024)](https://www.anthropic.com/engineering/building-effective-agents)
  — the agent-vs-workflow distinction and the "augmented LLM" building block.
