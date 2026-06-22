"""Level 1 · Lab 02 — The agent loop (ReAct), from scratch.

We turn a one-shot LLM into an agent by looping:
    Thought -> Action -> Action Input -> (we run the tool) -> Observation -> repeat
...until the model emits "Final Answer:".

Only ONE tool is used here (a calculator) so the focus stays on the loop itself.
Lab 03 generalizes to many tools.

Run:
    uv run python levels/01-foundations/02-the-agent-loop/lab.py
"""

from __future__ import annotations

import ast
import operator

from shared import LLMClient, MissingCredentialsError, Tracer

# --------------------------------------------------------------------------- #
# The one tool for this lab: a SAFE arithmetic evaluator.
# We never use bare eval() — that would run arbitrary code. Instead we parse the
# expression into an AST and evaluate only a whitelist of arithmetic operators.
# --------------------------------------------------------------------------- #

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calc(expression: str) -> str:
    """Evaluate a pure-arithmetic expression safely; return the result as a string."""

    def _eval(node):
        if isinstance(node, ast.Constant):  # numbers
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("only numeric constants are allowed")
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(node.op)](_eval(node.operand))
        raise ValueError("unsupported expression")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
        return str(result)
    except Exception as exc:  # noqa: BLE001 - report any failure back to the agent
        return f"Error: could not evaluate {expression!r} ({exc})"


def execute_action(action: str, action_input: str) -> str:
    """Run the tool the agent chose and return an observation string."""
    if action == "calculator":
        return safe_calc(action_input)
    # Telling the agent about its mistake (instead of crashing) lets it recover.
    return f"Error: unknown tool {action!r}. The only tool is 'calculator'."


# --------------------------------------------------------------------------- #
# The ReAct prompt + parser.
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """You are a reasoning agent that solves problems step by step.

You have access to ONE tool:
  calculator(expression) - evaluates an arithmetic expression, e.g. "12 * (3 + 4)"

Respond using EXACTLY this format for each step:
Thought: <your reasoning about what to do next>
Action: calculator
Action Input: <the arithmetic expression to evaluate>

When you know the final answer, respond instead with:
Thought: <your reasoning>
Final Answer: <the answer>

Rules:
- Output only ONE step at a time (one Thought, then either an Action/Action Input
  OR a Final Answer). Do not write the Observation yourself.
- Use the calculator for all arithmetic; do not compute in your head.
"""


def parse_react_output(text: str) -> dict:
    """Parse one model step into a structured dict.

    Returns one of:
      {"type": "final",  "thought": str, "answer": str}
      {"type": "action", "thought": str, "action": str, "action_input": str}
      {"type": "incomplete", "raw": str}   # model didn't follow the format
    """
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
        return {
            "type": "action",
            "thought": thought,
            "action": fields["Action"],
            "action_input": fields["Action Input"],
        }
    return {"type": "incomplete", "raw": text}


# --------------------------------------------------------------------------- #
# The loop.
# --------------------------------------------------------------------------- #


def run_agent(
    question: str,
    llm: LLMClient,
    *,
    tracer: Tracer | None = None,
    max_steps: int = 6,
) -> str:
    """Run the ReAct loop until the agent answers or we hit max_steps."""
    tracer = tracer or Tracer()
    scratchpad = ""  # accumulates the agent's own steps + our observations

    for step in range(1, max_steps + 1):
        tracer.info(f"step {step}/{max_steps}")
        prompt = f"Question: {question}\n{scratchpad}"
        # stop=["Observation:"] makes the model hand control back to us before it
        # invents a tool result. WE produce the observation by running the tool.
        generation = llm.complete(
            [{"role": "user", "content": prompt}],
            system=SYSTEM_PROMPT,
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
            observation = execute_action(parsed["action"], parsed["action_input"])
            tracer.observation(observation)
            # Append the model's step AND our observation to the scratchpad, then resend.
            scratchpad += f"{generation.strip()}\nObservation: {observation}\n"
            continue

        # The model broke format. Nudge it and try again.
        tracer.info("model output did not match the expected format; nudging.")
        scratchpad += (
            f"{generation.strip()}\n"
            "Observation: Your response did not follow the required format. "
            "Reply with Thought + Action/Action Input, or Thought + Final Answer.\n"
        )

    return f"Stopped after {max_steps} steps without a final answer."


def main() -> None:
    llm = LLMClient()
    question = (
        "A book club has 4 members. Each reads 3 books a month. "
        "How many books does the club read in a year, in total?"
    )
    print(f"Question: {question}\n")
    answer = run_agent(question, llm)
    print(f"\nFinal answer: {answer}")


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
