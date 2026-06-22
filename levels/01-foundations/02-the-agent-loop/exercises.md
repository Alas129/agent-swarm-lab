# Exercises — The agent loop (ReAct)

## 1. Trace a run
Run `lab.py` and read the THOUGHT / ACTION / OBSERVATION trace. How many steps did it
take? Identify where the model's *reasoning* changed based on an *observation*.

## 2. Break the format on purpose
Temporarily weaken `SYSTEM_PROMPT` (remove the format rules) and re-run. Watch the
`incomplete` branch fire and the agent nudge itself. Why is feeding the error back to the
model better than raising an exception?

## 3. Why the stop sequence?
Remove `stop=["Observation:"]` from the `llm.complete` call. What happens? (The model
tends to hallucinate its own `Observation:` lines.) Explain why stopping there — and
producing the observation *yourself* — is essential.

## 4. Step limit
Lower `max_steps` to 1 and ask a problem that needs two calculations. Confirm it stops
gracefully. Why is a hard step limit non-negotiable in production agents?

## 5. Harden the parser
`parse_react_output` reads line-by-line. Find an input it mis-parses (e.g. a multi-line
`Action Input`, or `Action:` appearing inside the Thought text). Make it more robust and
add a test in `tests/`.

## Stretch
Add a second tool (e.g. `string_length`) by editing `execute_action` and the system
prompt. Notice the friction — that's exactly the problem the tool *registry* in Lab 03
solves.
