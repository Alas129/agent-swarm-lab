# LLM as reasoner

> **Level 1 · Lab 01** — Before agents, understand the one thing they're built from: a
> single LLM call. The model is a stateless function from text to text.

## Prerequisites

- [Level 0](../../00-orientation/README.md) done; `hello.py` runs.

## Learning objectives

After this lab you can:

- Describe an LLM as a **stateless next-token predictor** — same call, no memory of the last one.
- Use a **system prompt** to set role and behaviour.
- Explain what **temperature** does and why output isn't perfectly reproducible.
- Recognize why a *single* call isn't yet an "agent."

## Concept

A chat LLM is, mechanically, a function: you give it a list of messages, it returns the
next assistant message. It has **no memory** of previous calls — anything it "remembers"
is only what you put back into the messages (that's Lab 04). It doesn't take actions in
the world (that's Labs 02–03). On its own it just predicts text.

Two knobs matter immediately:

- **System prompt** — separate instructions that set the model's role and constraints for
  the whole exchange ("You are a terse math tutor.").
- **Temperature** — how much randomness is injected during generation. Lower → more
  focused/repeatable; higher → more varied. For Claude it ranges `0.0`–`1.0` and defaults
  to `1.0`. Note: **even at `0.0`, output is not guaranteed to be identical** across calls.

```
   messages ──►  [ LLM ]  ──►  next assistant message
   (+ system)                 (no state kept between calls)
```

This single call is Anthropic's "augmented LLM" building block. Everything in this
curriculum is structure wrapped around calls like this — loops (Lab 02), tools (Lab 03),
and memory (Lab 04).

## In this lab

`lab.py` runs three short demonstrations:

1. **Statelessness** — ask the model its previous answer; it can't know, because each call
   is independent.
2. **System prompt** — the same question answered as a "pirate" vs. a "math professor."
3. **Temperature** — the same creative prompt at `temperature=0.0` vs `1.0`, to *see*
   variability.

Run it:

```bash
uv run python levels/01-foundations/01-llm-as-reasoner/lab.py
```

(No API key? It prints setup instructions instead of crashing.)

## Under the hood (no magic)

The labs call `llm.complete(...)` from [`shared/llm.py`](../../../shared/llm.py) so they
don't re-type SDK boilerplate. But it's not a framework — it's a thin wrapper over the
Anthropic Messages API. Here's the entire from-scratch equivalent of one `complete` call:

```python
import anthropic

client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from the environment
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.0,                     # the knob from this lab
    system="You are a precise assistant.",  # optional system prompt
    messages=[{"role": "user", "content": "What is recursion?"}],
)
text = "".join(block.text for block in response.content if block.type == "text")
```

That's it. `LLMClient` just bundles this, adds a friendly "set your API key" error, and
gives us one place to swap providers later. Every later lab builds on calls like this.

## Try it

See [exercises.md](exercises.md).

## Sources

- [Anthropic, "Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents)
  — the "augmented LLM" as the core building block.
- [Anthropic Messages API — `temperature`](https://platform.claude.com/docs/en/api/messages)
  — range, default, and the note that `temperature=0` is not fully deterministic.
- [Anthropic prompt engineering — "Give Claude a role"](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/system-prompts)
  — using a system prompt to steer behaviour.
