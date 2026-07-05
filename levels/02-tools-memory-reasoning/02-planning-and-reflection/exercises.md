# Exercises — Planning & reflection

## 1. Inspect a plan
Run the plan-and-execute demo. Print the parsed `steps`. Did the model produce sensible,
ordered steps? Try a task where step 3 depends on step 1 — does passing earlier results
forward actually help?

## 2. One-shot vs. reflexion
Give `reflexion` a task that's easy to get subtly wrong (e.g. "list the prime numbers
between 1 and 20"). Compare a single `llm.complete` answer with the reflexion result. Did
the critique catch anything?

## 3. The critique needs teeth
`parse_verdict` trusts the model to say `VERDICT: FAIL` honestly. Models are often too
agreeable and pass bad answers. Strengthen the critique prompt (e.g. "be a harsh
reviewer; assume the answer is wrong until proven right"). Does pass-rate change?

## 4. Reflexion can loop forever without a cap
Remove the `max_iters` guard and imagine a task the model never satisfies. Why is the cap
essential? Add a "best-so-far" return that picks the attempt with the most-positive
critique rather than just the last one.

## 5. Combine the two
Wrap each *step* of `execute_plan` in a mini-reflexion (attempt + critique per step).
Where does this help, and where does it just multiply cost?

## Stretch
Read [Tree of Thoughts](https://arxiv.org/abs/2305.10601). Sketch how you'd extend
plan-and-execute to explore *multiple* candidate plans and pick the best — and estimate
the call-count blow-up.
