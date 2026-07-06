"""Level 2 · Lab 04 — RAG agent, from scratch (reusing shared/retrieval.py).

Retrieval-Augmented Generation: retrieve relevant passages, then answer ONLY from them,
with citations, and say "I don't know" when the knowledge base doesn't cover the question.

Run:
    uv run python levels/02-tools-memory-reasoning/04-rag-agent/lab.py
"""

from __future__ import annotations

from shared import LLMClient, MissingCredentialsError, Tracer
from shared.retrieval import VectorStore  # built from scratch in Lab 2.03

DONT_KNOW = "I don't know based on the provided context."


def build_rag_prompt(question: str, passages: list[str]) -> str:
    """Construct an 'open-book' prompt that constrains the model to the retrieved context."""
    if passages:
        context = "\n".join(f"[{i}] {p}" for i, p in enumerate(passages, 1))
    else:
        context = "(no relevant context was found)"
    return (
        "Answer the question using ONLY the context below. Cite the sources you use as "
        f'[n]. If the context does not contain the answer, reply exactly: "{DONT_KNOW}"\n\n'
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )


def rag_answer(
    llm: LLMClient,
    store: VectorStore,
    question: str,
    *,
    k: int = 3,
    tracer: Tracer | None = None,
) -> str:
    """Retrieve top-k relevant passages, then generate a grounded, cited answer."""
    tracer = tracer or Tracer()
    hits = store.search(question, k=k)
    # Only keep passages with non-zero similarity — never inject irrelevant context.
    passages = [doc.text for doc, score in hits if score > 0]
    tracer.info(f"retrieved {len(passages)} relevant passage(s)")
    for p in passages:
        tracer.observation(p)

    prompt = build_rag_prompt(question, passages)
    answer = llm.complete([{"role": "user", "content": prompt}], temperature=0.0)
    tracer.answer(answer)
    return answer


def build_knowledge_base() -> VectorStore:
    store = VectorStore()
    for fact in [
        "The Eiffel Tower is located in Paris and was completed in 1889.",
        "Mount Everest is the highest mountain above sea level, at 8,849 metres.",
        "The Python programming language was created by Guido van Rossum in 1991.",
        "Honey never spoils; archaeologists have found edible honey in ancient tombs.",
        "The Pacific Ocean is the largest and deepest of Earth's oceans.",
    ]:
        store.add(fact)
    return store


def main() -> None:
    llm = LLMClient()
    store = build_knowledge_base()

    for question in [
        "When was the Eiffel Tower completed?",   # answerable from the KB
        "What is the capital of Australia?",       # NOT in the KB -> should say "I don't know"
    ]:
        print(f"\nQuestion: {question}")
        print("Answer:", rag_answer(llm, store, question, k=2))


if __name__ == "__main__":
    try:
        main()
    except MissingCredentialsError as exc:
        print("Environment not ready yet:\n")
        print(exc)
