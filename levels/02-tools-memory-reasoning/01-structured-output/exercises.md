# Exercises — Structured output

## 1. Watch the repair loop
Run `lab.py` with `Tracer()` enabled (the default). Then make the schema demand a field
the paragraph doesn't contain (e.g. `"email": str`). Watch the loop retry and eventually
raise. Why is a bounded retry count important?

## 2. Add type coercion
The model often returns `"age": "36"` (a string). Extend `validate` (or add a
`coerce` step) to accept a numeric string for an `int` field by converting it. Where
should coercion live — before or after validation?

## 3. The bool/int trap
`isinstance(True, int)` is `True` in Python, so `validate` accepts `True` for an `int`
field. Reproduce this, then fix `validate` to reject booleans where an integer is wanted.
Add a test.

## 4. Nested schema
Support a nested object, e.g. `{"name": str, "address": {"city": str, "zip": str}}`.
Make `validate` recurse. How does the prompt description need to change?

## 5. Break the extractor
`extract_json` counts braces and ignores strings. Find an input where a `}` inside a
string value makes it return malformed JSON (e.g. `{"note": "a } brace"}`). Decide whether
to handle it or rely on `json.loads` to reject it — and justify your choice.

## Stretch
Read the [Anthropic Structured Outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
List two guarantees the native feature gives that this hand-rolled loop cannot.
