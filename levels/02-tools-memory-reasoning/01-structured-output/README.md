# Structured output

> **Level 2 · Lab 01** — Make the model return data your code can use: typed JSON,
> validated, with an automatic repair loop. Built from scratch.

## Prerequisites

- [Level 1 — Foundations](../../01-foundations/README.md). You can call a model, loop, and
  use tools.

## Learning objectives

After this lab you can:

- Explain why free-text output is fragile for programs and why **schemas** fix it.
- Extract a JSON object from a model response (even with prose or code fences around it).
- **Validate** parsed output against a schema and run a **repair loop** that feeds errors
  back to the model.
- Know when to reach for the provider's **native structured outputs** instead.

## Concept

Agents act on model output with code: `result["price"] * quantity`. If the model replies
"The price is about twelve dollars," your program breaks. You need **structured output** —
a response that conforms to a known shape (a schema).

The from-scratch recipe is a small loop:

```
   instruction + schema ─► [LLM] ─► text
                                     │  extract JSON
                                     ▼
                                  parse ──► validate ──► ✓ return object
                                     │           │
                                     └───────────┘ ✗ errors → feed back, retry
```

Three failure points to handle: the model wraps JSON in prose or ```code fences``` (so we
**extract**), the JSON is malformed (so we **parse** defensively), or it's valid JSON but
missing a field / wrong type (so we **validate** and **repair**).

### You usually shouldn't hand-roll this in production

This lab builds the loop by hand so you understand it. In production, prefer the
provider's **native structured outputs**, which *guarantee* schema conformance instead of
hoping-and-retrying: Anthropic's Structured Outputs and OpenAI's `strict: true`. Same
goal, stronger guarantee. You'll use those in Level 5.

## In this lab

`lab.py` implements `extract_json`, `validate`, and `get_structured` (the repair loop),
then extracts a typed profile from a messy paragraph. Run it:

```bash
uv run python levels/02-tools-memory-reasoning/01-structured-output/lab.py
```

## Under the hood (no magic)

Only `LLMClient`/`Tracer` come from `shared/` (unchanged from Level 1). The schema,
extraction, validation, and retry loop are plain Python in `lab.py` — no library. A
"schema" here is just a dict of `field -> python type`:

```python
schema = {"name": str, "age": int, "languages": list}
errors = [f"missing '{f}'" for f in schema if f not in obj]  # ...plus type checks
```

## Try it

See [exercises.md](exercises.md).

## Sources

- [Anthropic — Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  — native schema-constrained JSON (the production-grade version of this lab).
- [OpenAI — Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
  — `strict: true` schema adherence in the OpenAI API.
