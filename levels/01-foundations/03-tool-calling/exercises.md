# Exercises — Tool calling

## 1. Add a tool in one line
Write a `reverse_text` tool (returns the input reversed) and register it. Notice you only
touched `default_registry` — the prompt and loop pick it up automatically via
`registry.describe()` and `registry.names()`. That's the payoff of the abstraction.

## 2. Make a tool fail
Ask a question that makes the agent call `calculator` with nonsense (e.g. "calculate the
square root of a banana"). Watch `Tool.run` catch the exception and return it as an
Observation. Did the agent recover on the next step?

## 3. Unknown-tool recovery
Temporarily tell the agent (in the question) to use a tool called `weather`. Confirm
`registry.run` returns the "unknown tool" error listing available tools, and that the
agent then picks a real tool. Why is listing the available tools in the error helpful?

## 4. Grow the knowledge base
Add three facts to `_KB`. Ask a multi-hop question that needs a `search` followed by a
`calculator` step. Trace how the observation from step 1 feeds the reasoning in step 2.

## 5. Toward native tool use
Read the [Anthropic tool use docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).
List two concrete advantages of the provider's native `tool_use`/`tool_result` over the
text-parsing approach here (hint: schemas, parsing reliability, parallel calls).

## Stretch
Give each `Tool` a JSON-schema-style `parameters` field and have the agent emit JSON
arguments instead of a raw string. This is the bridge to native function calling in Level 5.
