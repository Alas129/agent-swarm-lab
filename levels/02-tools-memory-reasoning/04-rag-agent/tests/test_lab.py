"""Offline tests for Lab 2.04 — RAG agent."""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM
from shared import Tracer

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab2_04", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab
_spec.loader.exec_module(lab)

SILENT = Tracer(enabled=False)


# --- prompt construction ------------------------------------------------------

def test_build_prompt_includes_passages_and_question():
    prompt = lab.build_rag_prompt("Q?", ["passage one", "passage two"])
    assert "[1] passage one" in prompt
    assert "[2] passage two" in prompt
    assert "Q?" in prompt
    assert lab.DONT_KNOW in prompt  # the grounding guardrail is always present


def test_build_prompt_handles_no_passages():
    prompt = lab.build_rag_prompt("Q?", [])
    assert "no relevant context" in prompt
    assert lab.DONT_KNOW in prompt


# --- rag_answer end-to-end (real retrieval, scripted generation) -------------

def test_rag_answer_grounds_in_retrieved_context():
    store = lab.build_knowledge_base()
    llm = ScriptedLLM(["The Eiffel Tower was completed in 1889 [1]."])
    answer = lab.rag_answer(llm, store, "When was the Eiffel Tower completed?", k=2, tracer=SILENT)
    assert "1889" in answer
    # The prompt actually sent to the model must contain the retrieved Eiffel passage.
    sent = llm.calls[0]["messages"][0]["content"]
    assert "Eiffel Tower" in sent


def test_rag_answer_with_no_relevant_docs_passes_empty_context():
    # An empty store guarantees no retrieval (the toy embedder's hash collisions mean even
    # a nonsense query can spuriously match a populated store — a documented limitation).
    store = lab.VectorStore()
    llm = ScriptedLLM([lab.DONT_KNOW])
    answer = lab.rag_answer(llm, store, "anything at all", k=2, tracer=SILENT)
    assert answer == lab.DONT_KNOW
    # No relevant passages -> the prompt signals an empty context.
    assert "no relevant context" in llm.calls[0]["messages"][0]["content"]
