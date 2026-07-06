# Level 2 — Tools, Memory & Reasoning

Make a single agent **capable and reliable**. Level 1 gave you an agent that loops, calls
tools, and remembers a conversation. Level 2 adds the techniques that make it trustworthy:
structured output, deliberate reasoning, durable memory, and grounded answers.

## Prerequisites

- [Level 1 — Foundations](../01-foundations/README.md) completed. You can call a model,
  run a ReAct loop, define tools, and keep conversation memory.

## The labs (do them in order)

1. **[01 — Structured output](01-structured-output/README.md)** — get typed, validated JSON
   from the model, with a repair loop. Built from scratch; pointers to native structured outputs.
2. **[02 — Planning & reflection](02-planning-and-reflection/README.md)** — plan-and-execute
   and reflexion (self-critique + retry) as reliability strategies.
3. **[03 — Memory & embeddings](03-memory-and-embeddings/README.md)** — long-term memory via
   a from-scratch vector store and cosine similarity; short- vs long-term memory.
4. **[04 — RAG agent](04-rag-agent/README.md)** — retrieval-augmented generation: grounded,
   cited answers that admit "I don't know." Capstone; reuses the Lab 03 retriever.

## How to run

```bash
uv run python levels/02-tools-memory-reasoning/01-structured-output/lab.py
uv run pytest levels/02-tools-memory-reasoning      # all offline, no API key needed
```

## What you'll have built

A single agent that returns machine-usable output, reasons in deliberate steps, remembers
across sessions, and grounds its answers in retrieved evidence. Level 3 takes the next
leap: **multiple** agents working together.

## A note on the toy embedder

Labs 03–04 use a dependency-free `SimpleEmbedder` (word-overlap, not true meaning) so they
run offline. Every concept doc says so explicitly and points to real embedding models
(Voyage AI, OpenAI). The *pipelines* you build are identical with a real embedder swapped in.
