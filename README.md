# agent-swarm-lab

An experimental playground and study repository for exploring multi-agent
orchestrations, communication protocols, and collaborative AI frameworks.

This repo is a **hands-on curriculum**: read a concept, run the code, do the
exercises. It takes you from a single LLM call all the way to production multi-agent
systems — **beginner → professional** — in deliberate, in-depth steps.

## Philosophy

- **Build it before you import it.** Early levels implement the core mechanics — the
  agent loop, tool calling, message passing, orchestration — *from scratch* in plain
  Python, so you understand what frameworks do for you. Later levels graduate to the
  real frameworks (LangGraph, CrewAI, AutoGen/AG2, OpenAI Agents SDK, Anthropic Agent SDK).
- **Python to run, language-agnostic to learn.** Implementations are Python, but every
  lab pairs with a concept doc that explains the *idea* independent of any framework or
  language. See the [`concepts/`](concepts/) index.
- **Cite the source.** Every concept links to an official doc or primary paper. No
  unsourced claims. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **Run everything.** Every lab is runnable and (where it makes sense) unit-tested, so
  you can verify your understanding, not just read about it.

## The curriculum

| Level | Topic | Status |
|------:|-------|--------|
| 0 | [Orientation & Setup](levels/00-orientation/) | ✅ built |
| 1 | [Foundations — single agent](levels/01-foundations/) | ✅ built |
| 2 | [Tools, Memory & Reasoning](levels/02-tools-memory-reasoning/) | ✅ built |
| 3 | Multi-Agent Orchestration | 🔜 planned |
| 4 | Communication Protocols (MCP, A2A, FIPA-ACL) | 🔜 planned |
| 5 | Frameworks in Practice | 🔜 planned |
| 6 | Advanced & Production | 🔜 planned |

The full level-by-level breakdown lives in [ROADMAP.md](ROADMAP.md). Levels are built
**one in-depth section at a time**.

## Setup

Requires **Python 3.11+**. We use [uv](https://docs.astral.sh/uv/) (fast, reproducible),
but plain `pip` works too.

```bash
# 1. Install dependencies (creates a .venv automatically)
uv sync --extra dev          # or:  pip install -e ".[dev]"

# 2. Add your API key
cp .env.example .env         # then edit .env and paste your ANTHROPIC_API_KEY
```

Get an Anthropic key at <https://console.anthropic.com/settings/keys>. Anthropic Claude
is the default provider; the labs talk to a thin wrapper ([`shared/llm.py`](shared/llm.py))
so you can swap providers in one place.

## Running a lab

Each lab is a self-contained folder. Read its `README.md`, then run `lab.py`:

```bash
uv run python levels/01-foundations/02-the-agent-loop/lab.py
```

Labs degrade gracefully: with no API key set, they print setup instructions instead of
crashing. Run a level's tests to check your work:

```bash
uv run pytest levels/01-foundations
```

## How a lab is structured

```
levels/<level>/<lab>/
  README.md      # the concept: theory, diagram, when-to-use, and Sources
  lab.py         # a runnable, heavily-commented reference implementation
  exercises.md   # try-it-yourself tasks that extend the lab
  tests/         # pytest checks so you can self-verify
```

## Repository layout

```
shared/      reusable utilities every lab builds on (LLM client, tracer)
concepts/    the language-agnostic concept index + glossary
levels/      the curriculum, one folder per level
ROADMAP.md   the full plan and build status
```

## Contributing / extending

Want to add a lab or fill in a future level? See [CONTRIBUTING.md](CONTRIBUTING.md) for
the lab template, style, and the (mandatory) sourcing rules.

## License

See [LICENSE](LICENSE).
