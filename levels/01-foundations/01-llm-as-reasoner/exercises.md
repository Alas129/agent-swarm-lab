# Exercises — LLM as reasoner

Work through these in order. Each builds intuition you'll need in later labs.

## 1. Make the model "remember" (warm-up for Lab 04)
`demo_statelessness` shows the model can't recall a previous call. Make it succeed by
passing the earlier turns as `history` to `build_messages`. What exactly did you have to
include? (This is precisely what "memory" will automate in Lab 04.)

## 2. Feel the temperature
Run `demo_temperature` a few times. Do the `temperature=0.0` outputs ever differ? Per
Anthropic's docs, even temperature 0 is *not* fully deterministic — did you observe that?

## 3. Steer with a system prompt
Write a system prompt that makes the model answer **only in valid JSON** of the form
`{"answer": "..."}`. Then ask a question and confirm the shape. Where does this get
fragile? (Reliable structured output is a Level 2 topic.)

## 4. Single call vs. agent
Ask the model: "What is 47 × 89, and what's the current date?" Why might the arithmetic
be wrong, and why can't it know today's date? Write down which capability each gap needs —
you'll add them in Labs 02–04.

## Stretch
Add a `temperature` sweep (0.0, 0.5, 1.0) and print all results side by side. Which kinds
of prompts are sensitive to temperature, and which barely change?
