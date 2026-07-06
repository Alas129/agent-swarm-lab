"""Shared utilities reused across every lab in agent-swarm-lab.

Public surface:
    from shared import LLMClient, MissingCredentialsError, Tracer
"""

from shared.llm import LLMClient, MissingCredentialsError
from shared.retrieval import VectorStore, SimpleEmbedder, cosine
from shared.tracing import Tracer

__all__ = [
    "LLMClient",
    "MissingCredentialsError",
    "Tracer",
    "VectorStore",
    "SimpleEmbedder",
    "cosine",
]
