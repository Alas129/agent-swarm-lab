"""Level 2 · Lab 03 — Memory & embeddings, from scratch.

Long-term memory = store text as vectors, retrieve by meaning (cosine similarity).
We build cosine, a toy embedder, a vector store, and a LongTermMemory wrapper — all
offline, no API key. The SAME components are packaged in shared/retrieval.py for reuse
in Lab 2.04 (RAG).

Run:
    uv run python levels/02-tools-memory-reasoning/03-memory-and-embeddings/lab.py
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
# 1. Cosine similarity — the angle between two vectors, in [-1, 1].
# --------------------------------------------------------------------------- #


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# --------------------------------------------------------------------------- #
# 2. A TOY embedder. Hashes word tokens into a fixed-length vector.
#    Deterministic + offline, but only captures word overlap, NOT meaning.
#    Real systems use Voyage AI (Anthropic's recommendation) or OpenAI.
# --------------------------------------------------------------------------- #

# Drop ultra-common words so they don't dominate the vector. A real embedding model
# would not need this; it's a band-aid for the toy approach.
_STOPWORDS = {"the", "a", "an", "of", "is", "are", "to", "in", "on", "and", "me", "my",
              "about", "tell", "what", "which", "who", "how", "does", "do", "has", "have"}


class SimpleEmbedder:
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            if token in _STOPWORDS:
                continue
            # hashlib, not built-in hash(), so buckets are stable across runs.
            bucket = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
            vec[bucket] += 1.0
        return vec


# --------------------------------------------------------------------------- #
# 3. A vector store: add texts, search by similarity.
# --------------------------------------------------------------------------- #


@dataclass
class Document:
    text: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)


class VectorStore:
    def __init__(self, embedder: SimpleEmbedder | None = None) -> None:
        self.embedder = embedder or SimpleEmbedder()
        self.documents: list[Document] = []

    def add(self, text: str, metadata: dict | None = None) -> None:
        self.documents.append(Document(text, self.embedder.embed(text), metadata or {}))

    def search(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        qv = self.embedder.embed(query)
        scored = [(doc, cosine(qv, doc.vector)) for doc in self.documents]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]


# --------------------------------------------------------------------------- #
# 4. LongTermMemory: a thin, intention-revealing wrapper over the store.
#    (Contrast: SHORT-term memory is just the recent-turns list from Level 1 Lab 04.)
# --------------------------------------------------------------------------- #


class LongTermMemory:
    def __init__(self) -> None:
        self.store = VectorStore()

    def remember(self, fact: str) -> None:
        self.store.add(fact)

    def recall(self, query: str, k: int = 3) -> list[str]:
        return [doc.text for doc, score in self.store.search(query, k) if score > 0]


def main() -> None:
    memory = LongTermMemory()
    facts = [
        "Mars has two moons named Phobos and Deimos.",
        "The Great Barrier Reef is the largest coral reef system on Earth.",
        "Python was first released in 1991 by Guido van Rossum.",
        "Jupiter is the largest planet in the solar system.",
        "The speed of light is about 299,792 kilometres per second.",
    ]
    for f in facts:
        memory.remember(f)

    for query in ["tell me about the moons of Mars", "which planet is biggest"]:
        print(f"\nQuery: {query!r}")
        for hit in memory.recall(query, k=2):
            print("  recalled:", hit)

    print(
        "\nNote: recall here works by WORD OVERLAP (toy embedder). A query like "
        "'red planet satellites' would miss the Mars fact, because the toy embedder "
        "doesn't know those words are related. A real embedding model would catch it."
    )


if __name__ == "__main__":
    main()
