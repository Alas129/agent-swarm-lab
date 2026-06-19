"""Level 1 · Lab 01 — LLM as reasoner.

Three tiny demonstrations of what a single LLM call is (and isn't):
  1. statelessness   — the model has no memory of previous calls
  2. system prompts  — set role/behaviour for the whole exchange
  3. temperature     — control randomness; see output vary

Run:
    uv run python levels/01-foundations/01-llm-as-reasoner/lab.py
"""

from shared import LLMClient, MissingCredentialsError


def build_messages(question: str, history: list[dict] | None = None) -> list[dict]:
    """Assemble the messages list for a single call.

    This is the *only* place state can live: a model call knows nothing except the
    messages you hand it. ``history`` lets the caller decide what (if anything) to
    carry over — foreshadowing Lab 04 (memory). Pure function → easy to unit test.
    """
    messages = list(history or [])
    messages.append({"role": "user", "content": question})
    return messages


def demo_statelessness(llm: LLMClient) -> None:
    print("\n=== 1. Statelessness ===")
    # First call.
    llm.complete(build_messages("My favourite number is 7. Acknowledge in 3 words."))
    # Second call with NO history — the model cannot know the previous turn.
    answer = llm.complete(
        build_messages("What was my favourite number? If you can't know, say so.")
    )
    print("Model (no history provided):", answer)
    print("→ It can't know: each call is independent. Memory = what YOU pass back in.")


def demo_system_prompt(llm: LLMClient) -> None:
    print("\n=== 2. System prompt steers behaviour ===")
    question = "In one sentence, what is recursion?"
    for role in ("You are a cheerful pirate.", "You are a precise computer-science professor."):
        answer = llm.complete(build_messages(question), system=role, temperature=0.0)
        print(f"[{role}]\n  {answer}")


def demo_temperature(llm: LLMClient) -> None:
    print("\n=== 3. Temperature controls randomness ===")
    prompt = "Invent a one-line name for a coffee shop on Mars."
    print("temperature=0.0 (focused):")
    for _ in range(2):
        print("  -", llm.complete(build_messages(prompt), temperature=0.0))
    print("temperature=1.0 (varied):")
    for _ in range(2):
        print("  -", llm.complete(build_messages(prompt), temperature=1.0))
    print("→ Lower temperature is more repeatable, but never a hard guarantee.")


def main() -> None:
    llm = LLMClient()
    demo_statelessness(llm)
    demo_system_prompt(llm)
    demo_temperature(llm)


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
