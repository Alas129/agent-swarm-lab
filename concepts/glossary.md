# Glossary

Short, sourced definitions of recurring terms. Each entry links to an authoritative
source. Terms grow as the curriculum does.

### Agent
A system that uses an LLM to **dynamically direct its own process and tool usage**,
deciding in a loop what to do next rather than following a fixed, predefined path. Anthropic
contrasts *agents* (the LLM controls the flow) with *workflows* (LLM and tools orchestrated
through predefined code paths).
— [Anthropic, "Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents)

### Workflow
A system where LLMs and tools are orchestrated through **predefined code paths**. Contrast
with an *agent*, which decides its own path at runtime.
— [Anthropic, "Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents)

### Agent loop
The repeated cycle an agent runs — reason about the goal, take an action, observe the
result, repeat — until it produces a final answer. The ReAct formulation interleaves
reasoning traces and actions.
— [Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)](https://arxiv.org/abs/2210.03629)

### ReAct
A prompting paradigm that has the model generate interleaved **rea**soning traces and
task **act**ions, so reasoning helps it plan/track actions and actions let it gather new
information from the environment.
— [Yao et al. (2022)](https://arxiv.org/abs/2210.03629)

### Tool use (function calling)
A capability where the model is given definitions of external tools (functions) and can
request that they be called with structured arguments; your code executes the tool and
returns the result to the model.
— [Anthropic tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
· [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)

### Token
The unit of text an LLM reads and generates (roughly a word-piece). Prompt length, memory,
and cost are all measured in tokens, and a model's **context window** is a fixed maximum
number of tokens.
— [Anthropic glossary](https://platform.claude.com/docs/en/docs/about-claude/glossary)

### Context window
The maximum number of tokens a model can attend to at once (prompt + generated output).
Conversation memory must fit within it, which is why long histories get summarized or
truncated.
— [Anthropic glossary](https://platform.claude.com/docs/en/docs/about-claude/glossary)

### System prompt
Instructions provided separately from the conversation that set the model's role,
constraints, and behaviour for the whole exchange ("Give Claude a role").
— [Anthropic prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/system-prompts)

### Temperature
A sampling parameter controlling randomness in generation: lower values make output more
deterministic/focused, higher values more varied. (Set to 0 for near-deterministic output.)
— [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages)
