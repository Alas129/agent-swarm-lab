"""Shared utilities reused across every lab in agent-swarm-lab.

Public surface:
    from shared import LLMClient, MissingCredentialsError, Tracer
"""

from shared.llm import LLMClient, MissingCredentialsError
from shared.tracing import Tracer

__all__ = ["LLMClient", "MissingCredentialsError", "Tracer"]
