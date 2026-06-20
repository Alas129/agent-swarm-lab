"""A tiny, provider-agnostic LLM client used by every lab.

Why this exists
---------------
Labs should teach *agent* concepts, not provider SDK boilerplate. So the labs talk
to this one small wrapper, and the wrapper talks to a provider. Swapping providers
(or mocking the client in tests) then happens in exactly one place.

Design notes
------------
* The wrapper exposes ONE method, ``complete(...)``, which takes a list of messages
  and returns a plain string. That is deliberately minimal: the early labs implement
  tool-use, memory, and the agent loop *themselves*, on top of plain text completion,
  so you can see the mechanics instead of relying on a framework.
* Default provider is Anthropic Claude. An OpenAI adapter is intentionally left as a
  stub (a learning exercise) — see ``_complete_openai``.
* If no API key is configured, ``complete`` raises :class:`MissingCredentialsError`
  with setup instructions, rather than failing with an opaque SDK error. Labs catch
  this in their ``__main__`` block and print a friendly message.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    # Loads variables from a local .env file if present. Optional at runtime.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is a declared dependency
    pass


# Default model ids. Override via env (ASL_DEFAULT_MODEL / ASL_CHEAP_MODEL) or the
# LLMClient constructor. Keep these current with the provider's model list.
DEFAULT_MODEL = os.environ.get("ASL_DEFAULT_MODEL", "claude-sonnet-4-6")
CHEAP_MODEL = os.environ.get("ASL_CHEAP_MODEL", "claude-haiku-4-5")


class MissingCredentialsError(RuntimeError):
    """Raised when a provider API key is not configured.

    Carries a human-readable hint so labs can print actionable setup steps.
    """


@dataclass
class Message:
    """A single chat turn. ``role`` is "user" or "assistant"; ``content`` is text."""

    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


def _normalize(messages) -> list[dict[str, str]]:
    """Accept either ``Message`` objects or plain ``{"role", "content"}`` dicts."""
    out: list[dict[str, str]] = []
    for m in messages:
        if isinstance(m, Message):
            out.append(m.as_dict())
        elif isinstance(m, dict) and "role" in m and "content" in m:
            out.append({"role": m["role"], "content": m["content"]})
        else:
            raise TypeError(
                "Each message must be a Message or a dict with 'role' and 'content', "
                f"got: {m!r}"
            )
    return out


class LLMClient:
    """Thin wrapper over a chat-completion provider.

    Example
    -------
    >>> llm = LLMClient()
    >>> llm.complete([{"role": "user", "content": "Say hi in one word."}])
    'Hi'
    """

    def __init__(
        self,
        model: str | None = None,
        provider: str = "anthropic",
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> None:
        self.provider = provider
        self.model = model or DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None  # lazily created on first use

    def complete(
        self,
        messages,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
    ) -> str:
        """Send ``messages`` and return the assistant's reply as a string.

        ``messages`` is a list of ``Message`` or ``{"role", "content"}`` dicts.
        ``system`` is an optional system prompt. ``stop`` is an optional list of
        stop sequences (useful for the ReAct loop, which stops at "Observation:").
        """
        msgs = _normalize(messages)
        temperature = self.temperature if temperature is None else temperature
        max_tokens = self.max_tokens if max_tokens is None else max_tokens

        if self.provider == "anthropic":
            return self._complete_anthropic(msgs, system, temperature, max_tokens, stop)
        if self.provider == "openai":
            return self._complete_openai(msgs, system, temperature, max_tokens, stop)
        raise ValueError(f"Unknown provider: {self.provider!r}")

    # -- providers ---------------------------------------------------------

    def _complete_anthropic(self, msgs, system, temperature, max_tokens, stop) -> str:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise MissingCredentialsError(
                "ANTHROPIC_API_KEY is not set.\n"
                "  1. Copy .env.example to .env\n"
                "  2. Add your key from https://console.anthropic.com/settings/keys\n"
                "  3. Re-run this lab."
            )
        if self._client is None:
            import anthropic  # imported lazily so `import shared` is cheap

            self._client = anthropic.Anthropic()

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": msgs,
        }
        if system is not None:
            kwargs["system"] = system
        if stop:
            kwargs["stop_sequences"] = stop

        response = self._client.messages.create(**kwargs)
        # A Messages API response is a list of content blocks; join the text blocks.
        parts = [block.text for block in response.content if block.type == "text"]
        return "".join(parts).strip()

    def _complete_openai(self, msgs, system, temperature, max_tokens, stop) -> str:
        # LEARNING EXERCISE (Level 5): implement this adapter.
        # The shape mirrors _complete_anthropic:
        #   * read OPENAI_API_KEY (raise MissingCredentialsError if absent)
        #   * `from openai import OpenAI; client = OpenAI()`
        #   * prepend {"role": "system", "content": system} to msgs if system is set
        #   * client.chat.completions.create(model=..., messages=..., stop=stop, ...)
        #   * return response.choices[0].message.content.strip()
        raise NotImplementedError(
            "The OpenAI adapter is a deliberate stub. Implementing it is an exercise "
            "in Level 5 (Frameworks in Practice). See the comments in shared/llm.py."
        )


__all__ = ["LLMClient", "Message", "MissingCredentialsError", "DEFAULT_MODEL", "CHEAP_MODEL"]
