"""Level 2 · Lab 02 — Planning & reflection, from scratch.

Two reasoning strategies built as orchestration around plain LLM calls:
  * plan-and-execute : make a plan, then run each step with earlier results in context
  * reflexion        : answer -> self-critique -> retry with the critique as a lesson

Run:
    uv run python levels/02-tools-memory-reasoning/02-planning-and-reflection/lab.py
"""

from __future__ import annotations

import re

from shared import LLMClient, MissingCredentialsError, Tracer

# --------------------------------------------------------------------------- #
# Plan-and-execute
# --------------------------------------------------------------------------- #


def parse_plan(text: str) -> list[str]:
    """Extract steps from a numbered list ('1. ...', '2) ...'), ignoring other prose."""
    steps = []
    for line in text.splitlines():
        match = re.match(r"\s*\d+[.)]\s+(.*)", line)
        if match and match.group(1).strip():
            steps.append(match.group(1).strip())
    return steps


def make_plan(llm: LLMClient, task: str, *, tracer: Tracer | None = None) -> list[str]:
    tracer = tracer or Tracer()
    text = llm.complete(
        [{"role": "user", "content":
          f"Break this task into a short numbered list of concrete steps.\n"
          f"Reply with ONLY the numbered list.\n\nTask: {task}"}],
        temperature=0.0,
    )
    steps = parse_plan(text)
    tracer.info(f"plan has {len(steps)} steps")
    return steps


def execute_plan(
    llm: LLMClient, task: str, steps: list[str], *, tracer: Tracer | None = None
) -> str:
    """Run each step with previous step results in context, then synthesize an answer."""
    tracer = tracer or Tracer()
    results: list[str] = []
    for i, step in enumerate(steps, 1):
        tracer.action(f"step {i}", step)
        prior = "\n".join(f"  Step {j}: {s} -> {r}" for j, (s, r) in
                          enumerate(zip(steps, results), 1))
        prompt = (
            f"Task: {task}\n"
            f"Results so far:\n{prior or '  (none yet)'}\n\n"
            f"Now perform step {i}: {step}\nGive only the result of this step."
        )
        result = llm.complete([{"role": "user", "content": prompt}], temperature=0.0)
        tracer.observation(result)
        results.append(result)

    summary = "\n".join(f"  Step {j}: {r}" for j, r in enumerate(results, 1))
    final = llm.complete(
        [{"role": "user", "content":
          f"Task: {task}\nStep results:\n{summary}\n\nGive the final answer to the task."}],
        temperature=0.0,
    )
    tracer.answer(final)
    return final


def plan_and_execute(llm: LLMClient, task: str, *, tracer: Tracer | None = None) -> str:
    tracer = tracer or Tracer()
    steps = make_plan(llm, task, tracer=tracer)
    return execute_plan(llm, task, steps, tracer=tracer)


# --------------------------------------------------------------------------- #
# Reflexion
# --------------------------------------------------------------------------- #


def parse_verdict(critique: str) -> bool:
    """True if the critique signals success (contains 'VERDICT: PASS')."""
    return "VERDICT: PASS" in critique.upper()


def reflexion(
    llm: LLMClient, task: str, *, max_iters: int = 3, tracer: Tracer | None = None
) -> str:
    """Generate -> critique -> retry, accumulating critiques as lessons, until PASS."""
    tracer = tracer or Tracer()
    lessons: list[str] = []
    attempt = ""

    for i in range(1, max_iters + 1):
        tracer.info(f"reflexion iteration {i}/{max_iters}")
        lesson_text = ("\nLessons from previous attempts:\n" + "\n".join(lessons)) if lessons else ""
        attempt = llm.complete(
            [{"role": "user", "content": f"Task: {task}{lesson_text}\n\nProvide your best answer."}],
            temperature=0.0,
        )
        tracer.thought(f"attempt: {attempt}")

        critique = llm.complete(
            [{"role": "user", "content":
              f"Task: {task}\nCandidate answer: {attempt}\n\n"
              "Critique this answer. If it is fully correct, end with 'VERDICT: PASS'. "
              "Otherwise explain what is wrong and end with 'VERDICT: FAIL'."}],
            temperature=0.0,
        )
        if parse_verdict(critique):
            tracer.answer(attempt)
            return attempt
        tracer.observation(f"rejected: {critique}")
        lessons.append(f"Attempt {i} was rejected because: {critique}")

    tracer.info(f"no PASS within {max_iters} iterations; returning last attempt")
    return attempt


def main() -> None:
    llm = LLMClient()
    print("=== Plan-and-execute ===")
    task = "Plan a simple 3-course dinner for 4 people with a vegetarian main, and list a shopping list."
    print("Task:", task, "\n")
    print("\nFinal:\n", plan_and_execute(llm, task))

    print("\n\n=== Reflexion ===")
    task2 = "Write a one-sentence definition of 'recursion' that is precise and does not use the word 'recursion'."
    print("Task:", task2, "\n")
    print("\nFinal:\n", reflexion(llm, task2))


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
