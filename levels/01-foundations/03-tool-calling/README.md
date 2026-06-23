# Tool calling

> **Level 1 · Lab 03** — Give the agent real tools. Build a `Tool` abstraction, a
> registry, dispatch, and error handling from scratch — the machinery frameworks hide.

## Prerequisites

- [Lab 02 — The agent loop](../02-the-agent-loop/README.md).

## Learning objectives

After this lab you can:

- Model a **tool** as `name + description + function`, and a **registry** of many tools.
- Generate the agent's system prompt from the registry, so adding a tool is one line.
- **Dispatch** the agent's chosen action to the right tool and feed the result back.
- Handle the two failure modes every tool-using agent hits: an **unknown tool** and a
  **tool that raises** — by returning the error to the model so it can recover.

## Concept

In Lab 02 the single tool was hard-coded into `execute_action`. That doesn't scale: each
new tool means editing the prompt *and* the dispatch logic, and one buggy tool can crash
the whole loop. The fix is a small abstraction:

```
        ┌─────────────┐        describe()         ┌────────────────────┐
        │  Registry   │ ───────────────────────►  │ system prompt lists │
        │  name→Tool  │                            │ every tool          │
        └─────┬───────┘                            └────────────────────┘
              │ run(name, input)
              ▼
   ┌──────────────────┐   func(input)   ┌──────────────┐
   │ Tool(name, desc, │ ──────────────► │ your Python  │
   │      func)       │ ◄────────────── │ function     │
   └──────────────────┘   result/error  └──────────────┘
```

The agent loop is unchanged from Lab 02 — only *where* the action goes changes: instead of
an `if/elif` it's `registry.run(action, action_input)`.

### Tool use is the high-leverage primitive — and frameworks do it for you

This lab parses tool calls out of the model's *text* (the original ReAct technique) so you
see the mechanics. Production providers expose this **natively**: you pass structured tool
schemas and the model returns a structured `tool_use` block (Anthropic) / `tool_call`
(OpenAI) that you execute and return as a `tool_result`. Same loop, sturdier plumbing.
You'll use the native APIs in Level 5.

## In this lab

`lab.py` defines `Tool`, `ToolRegistry`, three tools (`calculator`, `search` over a tiny
mock knowledge base, `word_count`), and a generalized `run_agent`. Run it:

```bash
uv run python levels/01-foundations/03-tool-calling/lab.py
```

## Under the hood (no magic)

The only `shared/` pieces here are `LLMClient` and `Tracer`, both unchanged from
[Lab 01](../01-llm-as-reasoner/README.md#under-the-hood-no-magic) and
[Lab 02](../02-the-agent-loop/README.md#under-the-hood-no-magic) — the same thin Anthropic
call and labelled prints.

Everything that's *new* in this lab — `Tool`, `ToolRegistry`, dispatch, and error
handling — is written from scratch in `lab.py`, with no `shared/` or framework
involvement. The registry is plain Python:

```python
class ToolRegistry:
    def __init__(self): self._tools = {}
    def register(self, tool): self._tools[tool.name] = tool
    def run(self, name, arg):
        tool = self._tools.get(name)
        return tool.run(arg) if tool else f"Error: unknown tool {name!r}."
```

## Try it

See [exercises.md](exercises.md).

## Sources

- [Anthropic — Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  — `tool_use` / `tool_result` blocks and the agentic loop, done natively.
- [OpenAI — Function calling](https://developers.openai.com/api/docs/guides/function-calling)
  — the same idea in the OpenAI API: tool schemas and structured tool calls.
- [Yao et al., "ReAct" (2022)](https://arxiv.org/abs/2210.03629) — parsing actions from
  the model's reasoning text, as we do here.
