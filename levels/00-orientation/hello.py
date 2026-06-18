"""Level 0 — environment check.

Runs a single LLM call to confirm your dependencies and ANTHROPIC_API_KEY work.
Run it with:

    uv run python levels/00-orientation/hello.py

With no API key set, it prints setup instructions instead of crashing — the same
graceful-degradation pattern every lab in this repo uses.
"""

from shared import LLMClient, MissingCredentialsError


def main() -> None:
    llm = LLMClient()
    reply = llm.complete(
        [{"role": "user", "content": "Reply with a friendly one-line hello for a learner "
                                     "starting an AI agents course."}]
    )
    print(reply)


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
