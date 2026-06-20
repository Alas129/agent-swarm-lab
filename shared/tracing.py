"""A dependency-free tracer for *seeing* what an agent does.

Multi-agent systems are hard to learn because the interesting behaviour happens
inside a loop you can't see. This tracer prints labelled, indented steps so you can
watch an agent think, act, and observe — the single most useful debugging habit in
this whole field.

Usage
-----
>>> t = Tracer()
>>> t.thought("I should add the numbers.")
>>> t.action("calculator", "2 + 2")
>>> t.observation("4")
>>> t.answer("The answer is 4.")

Disable all output (e.g. in tests) with ``Tracer(enabled=False)``.
"""

from __future__ import annotations

import sys

# ANSI colours, kept tiny and optional. Colour is disabled automatically when the
# output stream is not a TTY (e.g. piped to a file or captured by pytest).
_COLORS = {
    "thought": "\033[36m",  # cyan
    "action": "\033[33m",  # yellow
    "observation": "\033[35m",  # magenta
    "answer": "\033[32m",  # green
    "info": "\033[90m",  # grey
    "reset": "\033[0m",
}


class Tracer:
    """Pretty-prints the steps of an agent run."""

    def __init__(self, enabled: bool = True, color: bool | None = None, stream=None) -> None:
        self.enabled = enabled
        self.stream = stream or sys.stdout
        # Auto-detect colour support unless explicitly set.
        self.color = self.stream.isatty() if color is None else color

    def _emit(self, kind: str, label: str, content: str = "") -> None:
        if not self.enabled:
            return
        tag = f"[{label}]"
        if self.color:
            tag = f"{_COLORS.get(kind, '')}{tag}{_COLORS['reset']}"
        text = f"{tag} {content}" if content else tag
        print(text, file=self.stream)

    # -- the canonical ReAct step kinds ------------------------------------

    def thought(self, content: str) -> None:
        """The agent's private reasoning ('Thought:' in ReAct)."""
        self._emit("thought", "THOUGHT", content)

    def action(self, tool: str, tool_input: str = "") -> None:
        """A tool invocation the agent chose to make ('Action:' in ReAct)."""
        detail = f"{tool}({tool_input})" if tool_input else tool
        self._emit("action", "ACTION", detail)

    def observation(self, content: str) -> None:
        """The result returned by a tool ('Observation:' in ReAct)."""
        self._emit("observation", "OBSERVATION", content)

    def answer(self, content: str) -> None:
        """The agent's final answer to the user."""
        self._emit("answer", "ANSWER", content)

    def info(self, content: str) -> None:
        """A free-form note (step counter, warnings, etc.)."""
        self._emit("info", "INFO", content)


__all__ = ["Tracer"]
