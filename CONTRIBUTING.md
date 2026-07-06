# Contributing & extending agent-swarm-lab

This repo grows **one in-depth section at a time**. Whether you're adding a new lab,
fixing a bug, or filling in a future level, follow the conventions below so the
curriculum stays consistent and trustworthy.

## The golden rule: cite authentic sources

Every concept doc **must** end with a `## Sources` section that links **only**
official or primary references:

- Vendor/official docs (e.g. Anthropic, OpenAI, LangChain).
- Framework documentation.
- Primary research papers (prefer the arXiv abstract page or the publisher).

No blog-post paraphrases standing in for primary sources, and no unsourced claims.
**Verify links against the live source when you write them** — docs move (for example,
Anthropic docs now live on `platform.claude.com`). If a claim has no authoritative
source, either find one or don't make the claim.

## Lab anatomy

Each lab is a self-contained directory:

```
levels/<NN-level-name>/<NN-lab-name>/
  README.md      # the concept doc (see template below)
  lab.py         # runnable, heavily-commented reference implementation
  exercises.md   # try-it-yourself tasks that extend the lab
  tests/         # pytest checks (where it makes sense)
    test_<lab>.py
```

Naming: zero-padded numeric prefixes (`01-`, `02-`) keep folders in learning order.

### `README.md` (concept doc) template

```markdown
# <Lab title>

> **Level N · Lab NN** — one-sentence summary.

## Prerequisites
What the learner should have done first.

## Learning objectives
- Bullet goals: after this lab you can ...

## Concept
The idea, explained language- and framework-agnostically. Include a small diagram
(ASCII is fine) showing the data/control flow.

## In this lab
What `lab.py` actually does and how to run it.

## Under the hood (no magic)
A ~10-line snippet showing the from-scratch equivalent of whatever `shared/` utilities
this lab uses (the raw provider call behind `LLMClient`, the prints behind `Tracer`,
etc.). The point: `shared/` saves typing, it isn't doing anything you couldn't write
yourself. See "The `shared/` convention" below.

## Try it
Pointer to exercises.md.

## Sources
- [Title](https://official-url) — what it backs up.
```

### `lab.py` conventions

- Runnable standalone: `uv run python levels/.../lab.py`.
- Import shared utilities from `shared` (`from shared import LLMClient, Tracer`).
- Comment the *why*, not just the *what* — these files are teaching material.
- **Degrade gracefully without an API key.** Wrap the run in `__main__` and catch
  `MissingCredentialsError`, printing setup instructions instead of a stack trace.
- Keep provider specifics out of labs — go through `shared/llm.py`.

## The `shared/` convention (and "no magic")

Labs import a few utilities from [`shared/`](shared/) so each `lab.py` stays focused on
its concept instead of re-typing provider boilerplate:

| Utility | Used by | What it actually is |
|---------|---------|---------------------|
| `LLMClient` (`shared/llm.py`) | every lab that calls a model | a thin wrapper over the Anthropic Messages API |
| `Tracer` (`shared/tracing.py`) | labs that show an agent loop | labelled `print()` calls |
| `VectorStore`, `SimpleEmbedder`, `cosine` (`shared/retrieval.py`) | retrieval/RAG labs (Level 2+) | a toy embedder + in-memory cosine search (built from scratch in Level 2 · Lab 03) |
| `ScriptedLLM` (`shared/testing.py`) | `tests/` only | a fake client returning canned responses |

`LLMClient` is the only piece used by *every* lab; `Tracer` and `ScriptedLLM` are
per-need. Because labs import from `shared/`, a lab isn't standalone-copyable — the repo
must be installed (`uv sync`).

**The "no magic" rule:** so learners never mistake `shared/` for a framework doing
something mysterious, **every lab README includes an "Under the hood (no magic)" section**
showing the ~10-line from-scratch equivalent of the `shared/` bits that lab uses. `shared/`
saves typing; it is not a black box.

### `tests/` conventions

- Use `pytest`. Test the logic you can test **without a live LLM** (parsers, tool
  implementations, memory bookkeeping, loop control).
- For LLM-dependent paths, inject a fake client (`ScriptedLLM` from `shared/testing.py`,
  or any object with a `complete` method) rather than calling the network. Tests must
  pass offline.

## Updating the indexes

When you add a lab, also:

1. Add it to its level's `README.md`.
2. Link its concept doc from [`concepts/README.md`](concepts/README.md).
3. Add any new terms to [`concepts/glossary.md`](concepts/glossary.md) with a source.
4. Update [`ROADMAP.md`](ROADMAP.md) status when a level is complete.

## Environment

- Python 3.11+. Dependencies via `uv sync --extra dev` (or `pip install -e ".[dev]"`).
- Run a level's tests with `uv run pytest levels/<level>`.
