"""Offline tests for Lab 2.02 — planning & reflection."""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM
from shared import Tracer

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab2_02", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab
_spec.loader.exec_module(lab)

SILENT = Tracer(enabled=False)


# --- parsers ------------------------------------------------------------------

def test_parse_plan_numbered():
    text = "Here is the plan:\n1. Buy ingredients\n2) Cook\n3. Serve\nGood luck!"
    assert lab.parse_plan(text) == ["Buy ingredients", "Cook", "Serve"]


def test_parse_plan_ignores_nonnumbered():
    assert lab.parse_plan("- bullet\nsome prose\n1. real step") == ["real step"]


def test_parse_verdict():
    assert lab.parse_verdict("Looks great. VERDICT: PASS") is True
    assert lab.parse_verdict("Has a bug. VERDICT: FAIL") is False
    assert lab.parse_verdict("verdict: pass") is True  # case-insensitive


# --- plan-and-execute ---------------------------------------------------------

def test_make_plan():
    llm = ScriptedLLM(["1. first\n2. second"])
    assert lab.make_plan(llm, "task", tracer=SILENT) == ["first", "second"]


def test_execute_plan_threads_results_and_synthesizes():
    steps = ["compute a", "compute b"]
    # one call per step (2) + one synthesis call (1) = 3
    llm = ScriptedLLM(["result-A", "result-B", "FINAL ANSWER"])
    final = lab.execute_plan(llm, "task", steps, tracer=SILENT)
    assert final == "FINAL ANSWER"
    assert len(llm.calls) == 3
    # The step-2 prompt must include step-1's result.
    assert "result-A" in llm.calls[1]["messages"][0]["content"]
    # The synthesis prompt must include both results.
    assert "result-A" in llm.calls[2]["messages"][0]["content"]
    assert "result-B" in llm.calls[2]["messages"][0]["content"]


# --- reflexion ----------------------------------------------------------------

def test_reflexion_retries_then_passes():
    llm = ScriptedLLM(
        [
            "first attempt",                       # attempt 1
            "wrong because X. VERDICT: FAIL",      # critique 1
            "second attempt",                      # attempt 2
            "great. VERDICT: PASS",                # critique 2
        ]
    )
    result = lab.reflexion(llm, "task", max_iters=3, tracer=SILENT)
    assert result == "second attempt"
    assert len(llm.calls) == 4
    # Attempt 2 must include the lesson from the failed critique.
    assert "wrong because X" in llm.calls[2]["messages"][0]["content"]


def test_reflexion_returns_last_attempt_after_max_iters():
    # Always FAIL: 2 calls (attempt + critique) per iteration.
    llm = ScriptedLLM(
        [
            "a1", "bad. VERDICT: FAIL",
            "a2", "bad. VERDICT: FAIL",
        ]
    )
    result = lab.reflexion(llm, "task", max_iters=2, tracer=SILENT)
    assert result == "a2"
    assert len(llm.calls) == 4
