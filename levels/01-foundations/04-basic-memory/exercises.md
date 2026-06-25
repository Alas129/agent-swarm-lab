# Exercises — Basic memory

## 1. Prove statelessness vs. memory
Run `lab.py`. The "with memory" agent recalls the name; the "without memory" agent can't.
Explain in one sentence exactly what made the difference (hint: `memory.render()`).

## 2. Add a window
Create `Memory(max_messages=2)` and have a 4-turn conversation that refers back to turn 1.
Watch the agent "forget" the oldest turn once it falls out of the window. Why does the
real context window force *some* strategy like this?

## 3. The window can split a pair
With `max_messages=3`, trace which messages survive after several turns. Notice a window
can keep an assistant reply without its triggering user message. How would you fix that
(keep whole user/assistant *pairs*)? Implement it and add a test.

## 4. System prompt isn't memory
The `system` prompt is passed separately every call and isn't stored in `Memory`. Confirm
this in `ChatAgent.send`. Why is it good that the role instruction is *not* subject to the
window?

## 5. Estimate the budget
Add a `Memory.approx_tokens()` that estimates tokens as `len(text) / 4` (a rough rule of
thumb). Print it each turn and watch it climb. This is the quantity a real context window
limits.

## Stretch
Replace the sliding window with **summarization**: when memory exceeds N messages, call
the LLM to summarize the oldest turns into a single "summary" message you keep at the
front. This previews Level 2's memory strategies.
