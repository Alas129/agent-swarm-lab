"""Level 1 · Lab 04 — Basic memory, from scratch.

Memory is not a model feature — it's the conversation you accumulate and resend each
turn. Here we build:
  * Memory     — stores turns, with an optional sliding window (context-window analogy)
  * ChatAgent  — send(text): add turn -> call model with full memory -> store reply

Run:
    uv run python levels/01-foundations/04-basic-memory/lab.py
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared import LLMClient, MissingCredentialsError


@dataclass
class Memory:
    """Conversation memory: an ordered list of {"role", "content"} messages.

    ``max_messages`` is an optional sliding window. When set, only the most recent
    ``max_messages`` are kept — a deliberately simple stand-in for the real constraint,
    the model's finite context window. (Production systems summarize older turns instead
    of dropping them; that's Level 2.)
    """

    max_messages: int | None = None
    messages: list[dict] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self._apply_window()

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def _apply_window(self) -> None:
        if self.max_messages is not None and len(self.messages) > self.max_messages:
            # Keep only the most recent messages.
            self.messages = self.messages[-self.max_messages:]

    def render(self) -> list[dict]:
        """Return a copy of the messages to send to the model."""
        return list(self.messages)


class ChatAgent:
    """A minimal multi-turn chat agent backed by :class:`Memory`."""

    def __init__(self, llm: LLMClient, memory: Memory | None = None, system: str | None = None):
        self.llm = llm
        self.memory = memory or Memory()
        self.system = system

    def send(self, user_message: str) -> str:
        self.memory.add_user(user_message)
        reply = self.llm.complete(self.memory.render(), system=self.system, temperature=0.0)
        self.memory.add_assistant(reply)
        return reply


def demo_with_memory(llm: LLMClient) -> None:
    print("\n=== With memory (remembers across turns) ===")
    agent = ChatAgent(llm, system="You are a concise assistant.")
    print("U: My name is Sam and I love astronomy.")
    print("A:", agent.send("My name is Sam and I love astronomy."))
    print("U: What's my name and what do I love?")
    print("A:", agent.send("What's my name and what do I love?"))


def demo_without_memory(llm: LLMClient) -> None:
    print("\n=== Without memory (fresh each turn -> forgets) ===")
    # A brand-new agent per turn = no accumulated history.
    print("U: My name is Sam and I love astronomy.")
    print("A:", ChatAgent(llm).send("My name is Sam and I love astronomy."))
    print("U: What's my name and what do I love?")
    print("A:", ChatAgent(llm).send("What's my name and what do I love?"))


def main() -> None:
    llm = LLMClient()
    demo_with_memory(llm)
    demo_without_memory(llm)
    print("\n→ Same model, same questions. Only difference: what we resend.")


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
