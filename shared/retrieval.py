"""Reusable retrieval infrastructure: a toy embedder + an in-memory vector store.

This packages, for reuse by later labs, the same machinery you build from scratch in
Level 2 · Lab 03 (`02-tools-memory-reasoning/03-memory-and-embeddings`). The arc is the
repo's motto: *build it before you import it*, then graduate to the reusable version.

IMPORTANT — the embedder here is a TOY.
-----------------------------------------
``SimpleEmbedder`` hashes word tokens into a fixed-length vector. It is deterministic,
dependency-free, and offline, which makes it perfect for teaching and tests. But it only
captures **lexical overlap** (shared words), not **meaning**: "car" and "automobile" look
unrelated to it. Real systems use a trained embedding model — Anthropic recommends
**Voyage AI**; OpenAI also offers embeddings. Swapping is a one-line change: provide an
object with an ``embed(text) -> list[float]`` method.

Sources:
- Anthropic Embeddings (Voyage AI): https://platform.claude.com/docs/en/build-with-claude/embeddings
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors, in [-1, 1].

    cos = (a·b) / (|a| |b|). Returns 0.0 if either vector is all zeros.
    (Note: for length-normalized vectors like Voyage's, cosine == dot product.)
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# A few extremely common words carry no topical signal. Dropping them stops them from
# dominating the hashed vector (otherwise "the/of/is" overlap swamps real content words).
# A real embedding model needs no such hack — this is a toy-embedder band-aid.
_STOPWORDS = {
    "the", "a", "an", "of", "is", "are", "was", "were", "to", "in", "on", "and", "or",
    "for", "with", "at", "by", "it", "this", "that", "these", "those", "me", "my", "i",
    "you", "about", "tell", "what", "which", "who", "how", "does", "do", "did", "has",
    "have", "had", "be", "as", "from", "into",
}


def _tokenize(text: str) -> list[str]:
    """Lowercase content-word tokens (stopwords dropped). Trivial on purpose — see above."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS]


class SimpleEmbedder:
    """A deterministic, offline 'embedder' that hashes tokens into a fixed-dim vector.

    Real embedders learn semantics; this one only measures word overlap. It exists so the
    labs run with no API key and tests stay deterministic.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _bucket(self, token: str) -> int:
        # hashlib (not Python's built-in hash) so results are stable across processes.
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _tokenize(text):
            vec[self._bucket(token)] += 1.0
        return vec


@dataclass
class Document:
    """A stored item: its text, precomputed vector, and optional metadata."""

    text: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)


class VectorStore:
    """A minimal in-memory vector store: add texts, then search by semantic similarity."""

    def __init__(self, embedder: SimpleEmbedder | None = None) -> None:
        self.embedder = embedder or SimpleEmbedder()
        self.documents: list[Document] = []

    def add(self, text: str, metadata: dict | None = None) -> None:
        self.documents.append(
            Document(text=text, vector=self.embedder.embed(text), metadata=metadata or {})
        )

    def add_many(self, texts: list[str]) -> None:
        for t in texts:
            self.add(t)

    def search(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """Return the top-k (document, score) pairs by cosine similarity, best first."""
        query_vec = self.embedder.embed(query)
        scored = [(doc, cosine(query_vec, doc.vector)) for doc in self.documents]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]


__all__ = ["cosine", "SimpleEmbedder", "Document", "VectorStore"]
