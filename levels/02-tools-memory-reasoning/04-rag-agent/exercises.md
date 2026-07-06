# Exercises — RAG agent

## 1. Watch grounding work
Run `lab.py`. The first question is answerable from the KB; the second isn't. Confirm the
agent answers the first (with a citation) and refuses the second. Why is "I don't know"
better than a confident guess?

## 2. Retrieval is the ceiling
Ask "Who created Python?" — it works (word overlap). Now ask "Who invented the language
used for the demos here?" Does retrieval still find the Python fact? Explain why the toy
embedder makes or breaks the answer *before the LLM is even called*.

## 3. Tune k
Set `k=1` then `k=5`. With too-small `k` you miss relevant context; with too-large `k` you
stuff in noise (and pay more tokens). Find a failure case for each.

## 4. Show your sources
Change `rag_answer` to also return the list of passages it used, and print them next to the
answer. Verify the model's `[n]` citations actually match the passages.

## 5. Add a retriever tool to the Level 1 agent
Wrap `store.search` as a `Tool` (from Level 1 · Lab 03) and let the ReAct agent decide
*when* to retrieve, instead of always retrieving once. When is agentic retrieval better
than a fixed single retrieval step?

## Stretch
Swap the toy embedder for a real one (`VoyageEmbedder` from Lab 2.03 exercise 5) and re-run
exercise 2. Confirm semantic queries now work without shared words — the whole point of
real embeddings.
