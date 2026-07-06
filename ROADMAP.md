# Roadmap

The north-star arc for agent-swarm-lab: a beginner→professional path through agentic
and multi-agent systems. Levels are built **one in-depth section at a time** — a level
is marked ✅ only when its concept docs, runnable labs, exercises, tests, and sources
are all complete.

**Legend:** ✅ done · 🚧 in progress · 🔜 planned

---

## Level 0 — Orientation & Setup ✅

Get oriented and get the environment running.

- What an "agent" is, and how it differs from a plain workflow.
- The core agent loop, intuitively.
- Repo tour and a "hello, LLM" environment check.

*Primary source:* Anthropic, "Building effective agents."

## Level 1 — Foundations (single agent) ✅

Everything a single agent needs, built from scratch.

- `01-llm-as-reasoner` — one LLM call; prompting basics; temperature & determinism.
- `02-the-agent-loop` — the **ReAct** loop (think → act → observe → repeat), from scratch.
- `03-tool-calling` — give the agent tools; parse and execute actions, feed results back.
- `04-basic-memory` — short-term conversation memory; why and when it matters.

*Primary sources:* ReAct (Yao et al., 2022); Anthropic & OpenAI tool-use docs.

## Level 2 — Tools, Memory & Reasoning ✅

Make the single agent capable and reliable.

- `01-structured-output` — typed/validated JSON with a repair loop (from scratch).
- `02-planning-and-reflection` — plan-and-execute and Reflexion (self-critique + retry).
- `03-memory-and-embeddings` — cosine similarity, a vector store, long- vs short-term memory.
- `04-rag-agent` — retrieval-augmented generation: grounded, cited answers.

*Primary sources:* Structured outputs (Anthropic/OpenAI); Plan-and-Solve (Wang et al., 2023);
Reflexion (Shinn et al., 2023); Tree of Thoughts (Yao et al., 2023); RAG (Lewis et al., 2020);
Embeddings/Voyage (Anthropic).

## Level 3 — Multi-Agent Orchestration 🔜

Coordinate multiple agents. Build an orchestrator from scratch.

- Topologies: sequential, orchestrator-worker (hierarchical), parallel, debate, group chat.
- Roles, specialization, and handoffs.
- When multi-agent helps — and when it just adds cost and latency.

*Planned sources:* Anthropic "Building effective agents" (orchestrator-workers);
Anthropic multi-agent research system; AutoGen / MetaGPT / CAMEL papers.

## Level 4 — Communication Protocols 🔜

How agents (and tools) actually talk to each other.

- Message passing, blackboard / shared state, event-driven coordination.
- **MCP** (Model Context Protocol) — connecting agents to tools and data.
- **A2A** (Agent2Agent) — agent-to-agent interoperability.
- Classical grounding: **FIPA-ACL** agent communication language.

*Planned sources:* MCP spec (modelcontextprotocol.io); A2A spec; FIPA ACL specification.

## Level 5 — Frameworks in Practice 🔜

Solve the *same* multi-agent task across real frameworks; compare trade-offs.

- LangGraph, CrewAI, AutoGen / AG2, OpenAI Agents SDK, Anthropic Agent SDK.
- Implement the OpenAI adapter stub in `shared/llm.py` along the way.

*Planned sources:* each framework's official documentation.

## Level 6 — Advanced & Production 🔜

Operate agents in the real world.

- Evaluation & benchmarking; observability & tracing.
- Cost & latency; safety & guardrails; human-in-the-loop.
- Deployment and scaling agent swarms.

*Planned sources:* vendor production guides; eval frameworks; tracing tools.

---

## Build log

- **Level 0 + Level 1 + foundation** — initial build (scaffolding, shared utilities,
  concept index, orientation, and the four Foundations labs).
- **Level 2** — Tools, Memory & Reasoning: structured output, planning & reflection,
  memory & embeddings, and a RAG agent. Added `shared/retrieval.py` (vector store).
