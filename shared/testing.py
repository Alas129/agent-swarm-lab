"""Test helpers for labs — a scripted, offline stand-in for the LLM client.

Agent code in this repo depends on an object with a ``complete(...)`` method (see
:class:`shared.llm.LLMClient`). For tests we don't want to hit the network, so we inject
a ``ScriptedLLM`` that returns a queue of canned responses and records the calls it
received. This is the standard way to unit-test agent control flow deterministically.

Example
-------
>>> llm = ScriptedLLM(["Final Answer: 42"])
>>> llm.complete([{"role": "user", "content": "What is 6 * 7?"}])
'Final Answer: 42'
>>> llm.calls[0]["messages"][0]["content"]
'What is 6 * 7?'
"""

from __future__ import annotations


class ScriptedLLM:
    """A drop-in fake for :class:`shared.llm.LLMClient` driven by a list of responses.

    Each call to :meth:`complete` pops and returns the next queued response, and appends
    a record of the call (messages, system, stop) to :attr:`calls`.
    """

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def complete(
        self,
        messages,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
    ) -> str:
        self.calls.append(
            {"messages": messages, "system": system, "temperature": temperature, "stop": stop}
        )
        if not self.responses:
            raise AssertionError(
                "ScriptedLLM ran out of responses — the agent made more LLM calls than "
                "the test scripted. Add more responses or check the loop's termination."
            )
        return self.responses.pop(0)


__all__ = ["ScriptedLLM"]
