"""Offline tests for Lab 2.03 — memory & embeddings. Pure logic, no LLM."""

import importlib.util
import sys
from pathlib import Path

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab2_03", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab
_spec.loader.exec_module(lab)


# --- cosine -------------------------------------------------------------------

def test_cosine_identical_is_one():
    assert lab.cosine([1, 0, 0], [1, 0, 0]) == 1.0


def test_cosine_orthogonal_is_zero():
    assert lab.cosine([1, 0, 0], [0, 1, 0]) == 0.0


def test_cosine_zero_vector_is_zero():
    assert lab.cosine([0, 0], [1, 1]) == 0.0


def test_cosine_partial_overlap_between_zero_and_one():
    score = lab.cosine([1, 1, 0], [1, 0, 0])
    assert 0.0 < score < 1.0


# --- embedder -----------------------------------------------------------------

def test_embedder_is_deterministic():
    e = lab.SimpleEmbedder(dim=64)
    assert e.embed("hello world") == e.embed("hello world")


def test_embedder_dimension():
    assert len(lab.SimpleEmbedder(dim=128).embed("anything here")) == 128


def test_embedder_shared_words_are_similar():
    e = lab.SimpleEmbedder()
    a = e.embed("mars has moons")
    b = e.embed("the moons of mars")
    c = e.embed("pizza in rome")
    assert lab.cosine(a, b) > lab.cosine(a, c)


# --- VectorStore & LongTermMemory --------------------------------------------

def test_vector_store_ranks_relevant_first():
    store = lab.VectorStore()
    store.add("Mars has two moons named Phobos and Deimos.")
    store.add("The best pizza in Rome is debated endlessly.")
    results = store.search("how many moons does Mars have", k=2)
    assert "Mars" in results[0][0].text
    assert results[0][1] >= results[1][1]  # sorted best-first


def test_long_term_memory_recall_filters_zero_scores():
    mem = lab.LongTermMemory()
    mem.remember("Jupiter is the largest planet.")
    mem.remember("Python was released in 1991.")
    recalled = mem.recall("which planet is largest", k=5)
    assert any("Jupiter" in r for r in recalled)
    # An utterly unrelated query (no shared words) recalls nothing (all scores 0).
    assert mem.recall("zzqq xkcd qwerty") == []
