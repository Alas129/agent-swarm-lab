# Memory & embeddings

> **Level 2 · Lab 03** — Beyond the conversation window: give an agent **long-term memory**
> by storing text as vectors and retrieving it by *meaning*. Built from scratch.

## Prerequisites

- [Level 1 · Lab 04 — Basic memory](../../01-foundations/04-basic-memory/README.md)
  (short-term conversation memory and the context-window limit).

## Learning objectives

After this lab you can:

- Distinguish **short-term** memory (recent turns, kept in the context window) from
  **long-term** memory (a searchable store the agent queries on demand).
- Explain what an **embedding** is and how **cosine similarity** measures semantic closeness.
- Build a tiny **vector store** and a `LongTermMemory` that remembers and recalls by meaning.
- Understand why a *real* embedding model matters — and what a toy one can't do.

## Concept

Level 1's memory kept *recent* turns and dropped the rest. But an agent often needs a fact
from 500 turns ago, or from a document it read last week. That's **long-term memory**: store
everything, and *retrieve* only what's relevant to the current query.

To retrieve "by meaning," we turn text into **embeddings** — vectors where similar meanings
land near each other. Closeness is measured by **cosine similarity** (the angle between two
vectors): `1.0` = identical direction, `0.0` = unrelated.

```
 "Mars has two moons"  ──embed──► [0.1, 0.8, ...] ┐
 "the red planet's satellites" ─► [0.1, 0.7, ...] ┘ cosine ≈ 0.97  (close → relevant)
 "best pizza in Rome"  ──embed──► [0.9, 0.0, ...]   cosine ≈ 0.05  (far → irrelevant)

 query ─► embed ─► compare to every stored vector ─► return top-k
```

### A big honest caveat: our embedder is a toy

This lab's `SimpleEmbedder` hashes words into a vector. It's deterministic and runs with no
API key — perfect for learning — but it only sees **shared words**, not meaning. To it,
"car" and "automobile" are unrelated. **Real systems use a trained embedding model.**
Anthropic doesn't ship one and recommends **Voyage AI**; OpenAI offers embeddings too.
Swapping is one line: provide any object with `embed(text) -> list[float]`. (Handy fact
from Voyage's docs: their vectors are length-normalized, so cosine equals a plain dot product.)

## In this lab

`lab.py` builds `cosine`, `SimpleEmbedder`, `VectorStore`, and `LongTermMemory` from
scratch, then stores facts and recalls them by query. Run it:

```bash
uv run python levels/02-tools-memory-reasoning/03-memory-and-embeddings/lab.py
```

## Under the hood (no magic)

Everything is built from scratch in `lab.py` — cosine is three lines of arithmetic:

```python
def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    return dot / (math.hypot(*a) * math.hypot(*b))   # 0 if either is all-zeros
```

The *same* components are packaged in [`shared/retrieval.py`](../../../shared/retrieval.py)
for reuse — the next lab ([2.04 RAG](../04-rag-agent/README.md)) imports them instead of
re-typing. Build it from scratch here; reuse it there.

## Try it

See [exercises.md](exercises.md).

## Sources

- [Anthropic — Embeddings (Voyage AI)](https://platform.claude.com/docs/en/build-with-claude/embeddings)
  — Anthropic recommends Voyage; covers cosine vs. dot product on normalized vectors.
- [OpenAI — Function calling / embeddings docs](https://developers.openai.com/api/docs)
  — an alternative embeddings provider.
