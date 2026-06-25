# Basic memory

> **Level 1 · Lab 04** — LLMs are stateless between calls. Build conversation memory from
> scratch, and respect the finite **context window**.

## Prerequisites

- [Lab 01 — LLM as reasoner](../01-llm-as-reasoner/README.md) (statelessness).
- Labs 02–03 help, but this lab stands on its own.

## Learning objectives

After this lab you can:

- Explain why an agent "remembers" only what you resend, and build a `Memory` that does it.
- Wrap memory in a `ChatAgent` so multi-turn conversation just works.
- Implement a **window** (keep the last N messages) and explain why the **context window**
  forces a strategy when history grows.

## Concept

Lab 01 proved each model call is independent. So "memory" isn't a model feature — it's
something *you* build by accumulating the conversation and resending it every turn:

```
turn 1:  send [u1]                        -> a1     ; store u1, a1
turn 2:  send [u1, a1, u2]                -> a2     ; store u2, a2
turn 3:  send [u1, a1, u2, a2, u3]        -> a3     ; ...
                  └── grows every turn ──┘
```

That growth is the catch. A model has a fixed **context window** (a maximum number of
tokens it can attend to). You cannot resend an unbounded history forever, so real systems
**trim or summarize**. The simplest strategy — and the one we build here — is a sliding
**window**: keep only the most recent N messages. (Summarization and long-term/vector
memory are Level 2.)

## In this lab

`lab.py` implements:

- `Memory` — accumulates user/assistant turns, with an optional `max_messages` window.
- `ChatAgent` — `send(text)` adds the turn, calls the model with the full memory, stores
  the reply.

It then runs two demos: a stateful conversation that recalls an earlier fact, and the
same conversation with memory disabled (the model forgets). Run it:

```bash
uv run python levels/01-foundations/04-basic-memory/lab.py
```

## Under the hood (no magic)

This lab uses only `LLMClient`, unchanged from
[Lab 01](../01-llm-as-reasoner/README.md#under-the-hood-no-magic) (the thin Anthropic call).
`Memory` and `ChatAgent` are written from scratch in `lab.py` and are pure Python — memory
is just a list you resend:

```python
class Memory:
    def __init__(self): self.messages = []
    def add(self, role, content): self.messages.append({"role": role, "content": content})

# one chat turn = add user msg -> send the whole list -> store the reply
memory.add("user", text)
reply = llm.complete(memory.messages)   # the Lab 01 Anthropic call
memory.add("assistant", reply)
```

There is no hidden "memory feature" anywhere — not in `shared/`, not in the model. The
agent remembers exactly because you resend `memory.messages` every call.

## Try it

See [exercises.md](exercises.md).

## Sources

- [Anthropic glossary — context window & tokens](https://platform.claude.com/docs/en/docs/about-claude/glossary)
  — why history is bounded and measured in tokens.
- [Anthropic — Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
  — how the working-memory limit behaves in practice.
