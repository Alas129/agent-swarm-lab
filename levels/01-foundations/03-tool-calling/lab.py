"""Level 1 · Lab 03 — Tool calling, from scratch.

Generalizes Lab 02's single hard-coded tool into:
  * Tool          — name + description + a Python function
  * ToolRegistry  — a collection the agent can describe and dispatch to
  * run_agent     — the ReAct loop, now tool-agnostic (registry.run(...))

Run:
    uv run python levels/01-foundations/03-tool-calling/lab.py
"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Callable

from shared import LLMClient, MissingCredentialsError, Tracer

# --------------------------------------------------------------------------- #
# Tool + registry abstractions.
# --------------------------------------------------------------------------- #


@dataclass
class Tool:
    """A callable the agent can invoke: a name, a one-line description, a function."""

    name: str
    description: str
    func: Callable[[str], str]

    def run(self, tool_input: str) -> str:
        """Execute the tool, converting any exception into an observation string.

        Returning the error (instead of raising) is the whole game: the agent reads it
        as an Observation and can correct course on the next step.
        """
        try:
            return str(self.func(tool_input))
        except Exception as exc:  # noqa: BLE001 - surface failures to the agent
            return f"Error: tool {self.name!r} failed: {exc}"


class ToolRegistry:
    """A name→Tool map the agent can describe (for the prompt) and dispatch to."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def describe(self) -> str:
        """Render the tool list for the system prompt."""
        return "\n".join(f"  {t.name}(input) - {t.description}" for t in self._tools.values())

    def run(self, name: str, tool_input: str) -> str:
        tool = self.get(name)
        if tool is None:
            return (
                f"Error: unknown tool {name!r}. "
                f"Available tools: {', '.join(self.names())}."
            )
        return tool.run(tool_input)


# --------------------------------------------------------------------------- #
# The actual tools.
# --------------------------------------------------------------------------- #

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression (no bare eval)."""

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError("unsupported expression")

    return str(_eval(ast.parse(expression, mode="eval").body))


# A tiny mock "knowledge base" so search is deterministic and offline-testable.
_KB = {
    "speed of light": "The speed of light is 299,792,458 metres per second.",
    "mars": "Mars has two moons: Phobos and Deimos.",
    "python": "Python was first released in 1991 by Guido van Rossum.",
}


def search(query: str) -> str:
    """Look up a fact in a small mock knowledge base."""
    q = query.lower()
    for key, fact in _KB.items():
        if key in q:
            return fact
    return "No results found."


def word_count(text: str) -> str:
    """Count the words in the input text."""
    return str(len(text.split()))


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(Tool("calculator", "evaluate an arithmetic expression like '3 * (4+5)'", calculator))
    reg.register(Tool("search", "look up a fact by keyword in the knowledge base", search))
    reg.register(Tool("word_count", "count the number of words in the given text", word_count))
    return reg


# --------------------------------------------------------------------------- #
# The generalized ReAct loop (tool-agnostic).
# --------------------------------------------------------------------------- #


def build_system_prompt(registry: ToolRegistry) -> str:
    return f"""You are a helpful agent that solves tasks step by step using tools.

Available tools:
{registry.describe()}

Respond using EXACTLY this format for each step:
Thought: <your reasoning about what to do next>
Action: <one of: {', '.join(registry.names())}>
Action Input: <the input to the tool>

When you know the final answer, respond instead with:
Thought: <your reasoning>
Final Answer: <the answer>

Rules:
- One step at a time. Do not write the Observation yourself.
- Pick exactly one tool per Action, by its exact name.
"""


def parse_react_output(text: str) -> dict:
    """Parse one model step (same format as Lab 02)."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    fields: dict[str, str] = {}
    for line in lines:
        for key in ("Thought:", "Action Input:", "Action:", "Final Answer:"):
            if line.startswith(key):
                fields[key.rstrip(":")] = line[len(key):].strip()
                break
    thought = fields.get("Thought", "")
    if "Final Answer" in fields:
        return {"type": "final", "thought": thought, "answer": fields["Final Answer"]}
    if "Action" in fields and "Action Input" in fields:
        return {"type": "action", "thought": thought,
                "action": fields["Action"], "action_input": fields["Action Input"]}
    return {"type": "incomplete", "raw": text}


def run_agent(
    question: str,
    llm: LLMClient,
    registry: ToolRegistry,
    *,
    tracer: Tracer | None = None,
    max_steps: int = 6,
) -> str:
    """ReAct loop that dispatches actions through the tool registry."""
    tracer = tracer or Tracer()
    system = build_system_prompt(registry)
    scratchpad = ""

    for step in range(1, max_steps + 1):
        tracer.info(f"step {step}/{max_steps}")
        prompt = f"Question: {question}\n{scratchpad}"
        generation = llm.complete(
            [{"role": "user", "content": prompt}],
            system=system,
            stop=["Observation:"],
            temperature=0.0,
        )
        parsed = parse_react_output(generation)

        if parsed["type"] == "final":
            if parsed["thought"]:
                tracer.thought(parsed["thought"])
            tracer.answer(parsed["answer"])
            return parsed["answer"]

        if parsed["type"] == "action":
            tracer.thought(parsed["thought"])
            tracer.action(parsed["action"], parsed["action_input"])
            observation = registry.run(parsed["action"], parsed["action_input"])
            tracer.observation(observation)
            scratchpad += f"{generation.strip()}\nObservation: {observation}\n"
            continue

        tracer.info("output did not match format; nudging.")
        scratchpad += (
            f"{generation.strip()}\n"
            "Observation: Your response did not follow the format. Use Thought + "
            "Action/Action Input, or Thought + Final Answer.\n"
        )

    return f"Stopped after {max_steps} steps without a final answer."


def main() -> None:
    llm = LLMClient()
    registry = default_registry()
    question = (
        "How many words are in the search result about Mars, "
        "and what is that word count multiplied by 10?"
    )
    print(f"Question: {question}\n")
    answer = run_agent(question, llm, registry)
    print(f"\nFinal answer: {answer}")


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
