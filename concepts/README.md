# Concepts index

The language-agnostic track. Each lab in [`levels/`](../levels/) pairs runnable Python
with a concept doc that explains the *idea* independently of any framework or language.
This page aggregates and cross-links those concept docs, so you can read the theory as a
through-line or jump to the lab that implements it.

See also the [glossary](glossary.md) for quick term definitions with sources.

## Foundations (Level 1)

- [**LLM as reasoner**](../levels/01-foundations/01-llm-as-reasoner/README.md) — the model
  is a stateless next-token predictor; prompting, sampling, temperature, and determinism.
- [**The agent loop (ReAct)**](../levels/01-foundations/02-the-agent-loop/README.md) — turning
  a one-shot model into an agent by interleaving reasoning and acting in a loop.
- [**Tool calling**](../levels/01-foundations/03-tool-calling/README.md) — letting an agent
  act on the world: declaring tools, parsing the agent's chosen action, executing, and
  feeding results back.
- [**Basic memory**](../levels/01-foundations/04-basic-memory/README.md) — agents are
  stateless by default; how conversation memory is constructed and why context is finite.

## Coming next

Concept docs for Levels 2–6 (reasoning & planning, orchestration topologies, communication
protocols, frameworks, and production concerns) land as those sections are built. See the
[roadmap](../ROADMAP.md).
