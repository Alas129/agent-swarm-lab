"""Level 2 · Lab 01 — Structured output, from scratch.

Get typed, validated JSON out of a model, with an automatic repair loop:
    extract JSON -> parse -> validate against a schema -> on error, feed back and retry.

Run:
    uv run python levels/02-tools-memory-reasoning/01-structured-output/lab.py
"""

from __future__ import annotations

import json

from shared import LLMClient, MissingCredentialsError, Tracer

# A "schema" is just field name -> expected Python type. (Real schema languages like
# JSON Schema are richer; this is enough to teach the loop.)
_TYPE_NAMES = {str: "string", int: "integer", float: "number",
               bool: "boolean", list: "array", dict: "object"}


def extract_json(text: str) -> str | None:
    """Pull the first balanced {...} object out of a response, ignoring surrounding
    prose or ```code fences```. Returns the JSON substring, or None if there isn't one.

    (Brace-counting is simple and good enough here; it doesn't account for braces inside
    string values — see exercise 5.)
    """
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None  # never closed


def validate(obj: object, schema: dict[str, type]) -> list[str]:
    """Return a list of human-readable errors; empty list means valid."""
    if not isinstance(obj, dict):
        return ["top-level value must be a JSON object"]
    errors: list[str] = []
    for field, expected in schema.items():
        if field not in obj:
            errors.append(f"missing field '{field}'")
        elif not isinstance(obj[field], expected):
            got = type(obj[field]).__name__
            errors.append(f"field '{field}' should be {_TYPE_NAMES.get(expected, expected)}, got {got}")
    return errors


def describe_schema(schema: dict[str, type]) -> str:
    return ", ".join(f'"{f}" ({_TYPE_NAMES[t]})' for f, t in schema.items())


def get_structured(
    llm: LLMClient,
    instruction: str,
    schema: dict[str, type],
    *,
    max_retries: int = 2,
    tracer: Tracer | None = None,
) -> dict:
    """Ask the model for JSON matching `schema`, validating and repairing up to
    `max_retries` extra times. Raises ValueError if it never produces valid output.
    """
    tracer = tracer or Tracer()
    system = "You output ONLY a single JSON object. No prose, no markdown, no code fences."
    base_prompt = f"{instruction}\n\nReturn a JSON object with fields: {describe_schema(schema)}."
    feedback = ""

    errors: list[str] = []
    for attempt in range(1, max_retries + 2):  # 1 initial attempt + max_retries
        text = llm.complete(
            [{"role": "user", "content": base_prompt + feedback}],
            system=system,
            temperature=0.0,
        )
        raw = extract_json(text)
        if raw is None:
            obj, errors = None, ["no JSON object found in the response"]
        else:
            try:
                obj = json.loads(raw)
                errors = validate(obj, schema)
            except json.JSONDecodeError as exc:
                obj, errors = None, [f"invalid JSON: {exc}"]

        if obj is not None and not errors:
            tracer.info(f"valid structured output on attempt {attempt}")
            return obj

        tracer.info(f"attempt {attempt} failed: {errors}")
        # Feed the specific errors back so the model can repair its own output.
        feedback = (
            f"\n\nYour previous response had these problems: {errors}. "
            "Fix them and return ONLY the corrected JSON object."
        )

    raise ValueError(
        f"could not obtain valid structured output after {max_retries + 1} attempts; "
        f"last errors: {errors}"
    )


def main() -> None:
    llm = LLMClient()
    blurb = (
        "So this is Ada — she's 36, works mostly in Python and Rust these days, "
        "and has been coding since she was a teenager."
    )
    schema = {"name": str, "age": int, "languages": list}
    print("Input paragraph:\n ", blurb, "\n")
    result = get_structured(llm, f"Extract the person's details from: {blurb}", schema)
    print("Structured result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
