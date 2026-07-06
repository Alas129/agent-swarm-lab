# RAG agent

> **Level 2 · Lab 04** — Ground an agent's answers in a knowledge base it retrieves from,
> so it cites sources and admits when it doesn't know. The capstone of Level 2.

## Prerequisites

- [Lab 2.03 — Memory & embeddings](../03-memory-and-embeddings/README.md) (vector store,
  retrieval). We reuse it via `shared/retrieval.py`.
- [Level 1 — Foundations](../../01-foundations/README.md) (calling a model).

## Learning objectives

After this lab you can:

- Explain **Retrieval-Augmented Generation (RAG)**: retrieve relevant text, then generate
  an answer *conditioned on it*.
- Build a RAG pipeline: index documents → retrieve top-k for a query → stuff them into the
  prompt → generate a grounded, cited answer.
- Make the agent **say "I don't know"** when the knowledge base lacks the answer — the
  single most important guardrail against hallucination.

## Concept

A bare LLM answers from its frozen training data: it can't cite sources, doesn't know your
private documents, and will confidently make things up. **RAG** fixes this by retrieving
relevant passages first and asking the model to answer *only* from them:

```
 question ─► retrieve top-k from vector store ─► passages
                                                   │
              ┌────────────────────────────────────┘
              ▼
   prompt = "Answer using ONLY this context, cite [n],
             say 'I don't know' if it's not here:" + passages + question
              │
              ▼
            [LLM] ─► grounded, cited answer
```

This is "open-book" answering. The retrieval step ([Lab 2.03](../03-memory-and-embeddings/README.md))
decides *what the model gets to see*; the prompt decides *how strictly it must stay within it*.

> ⚠️ **Reminder:** this lab uses the toy `SimpleEmbedder` from Lab 2.03, so retrieval is by
> word overlap, not true meaning. Real RAG quality lives or dies on a good embedding model
> (Voyage AI / OpenAI). The *pipeline* you build here is exactly the same either way.

## In this lab

`lab.py` indexes a small knowledge base into a `VectorStore` (from `shared/retrieval.py`),
then `rag_answer` retrieves, builds a grounded prompt, and generates. Run it:

```bash
uv run python levels/02-tools-memory-reasoning/04-rag-agent/lab.py
```

## Under the hood (no magic)

The retrieval machinery is imported from
[`shared/retrieval.py`](../../../shared/retrieval.py) — the very code you built from scratch
in Lab 2.03 (the "graduate to reuse" step). RAG itself is just prompt construction:

```python
passages = [doc.text for doc, score in store.search(question, k) if score > 0]
prompt = "Answer using ONLY this context, cite [n], else say I don't know:\n" + passages
answer = llm.complete(prompt)
```

No RAG framework — retrieve, stuff, generate.

## Try it

See [exercises.md](exercises.md).

## Sources

- [Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)](https://arxiv.org/abs/2005.11401)
  — the paper that introduced RAG.
- [Anthropic — Embeddings & RAG](https://platform.claude.com/docs/en/build-with-claude/embeddings)
  — embeddings for retrieval, plus a pointer to Anthropic's RAG cookbook.
