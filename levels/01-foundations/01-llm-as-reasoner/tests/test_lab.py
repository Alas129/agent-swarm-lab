"""Offline tests for Lab 01. No network: we inject a ScriptedLLM.

These tests pin down the one piece of real logic in the lab — how messages are
assembled — and verify the lab talks to the client the way we expect.
"""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM

# Load lab.py by path (labs are scripts, not importable packages).
_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab01", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab  # register so importlib-loaded module resolves cleanly
_spec.loader.exec_module(lab)


def test_build_messages_appends_question():
    msgs = lab.build_messages("hello")
    assert msgs == [{"role": "user", "content": "hello"}]


def test_build_messages_includes_history_in_order():
    history = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "ok"},
    ]
    msgs = lab.build_messages("second", history=history)
    assert [m["content"] for m in msgs] == ["first", "ok", "second"]
    # The original history list must not be mutated.
    assert len(history) == 2


def test_build_messages_does_not_mutate_history():
    history = [{"role": "user", "content": "x"}]
    lab.build_messages("y", history=history)
    assert history == [{"role": "user", "content": "x"}]


def test_demo_statelessness_makes_two_independent_calls():
    llm = ScriptedLLM(["acknowledged ok now", "I cannot know that."])
    lab.demo_statelessness(llm)
    # Two calls were made, and the second carried NO history (statelessness).
    assert len(llm.calls) == 2
    assert len(llm.calls[1]["messages"]) == 1
