"""Offline tests for Lab 02 — the ReAct loop. No network: we script the LLM."""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM
from shared import Tracer

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab02", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab  # register so importlib-loaded module resolves cleanly
_spec.loader.exec_module(lab)

SILENT = Tracer(enabled=False)


# --- safe_calc ----------------------------------------------------------------

def test_safe_calc_basic():
    assert lab.safe_calc("2 + 2") == "4"
    assert lab.safe_calc("12 * (3 + 4)") == "84"
    assert lab.safe_calc("2 ** 10") == "1024"


def test_safe_calc_rejects_code_injection():
    # bare eval would run this; safe_calc must not.
    out = lab.safe_calc("__import__('os').system('echo hi')")
    assert out.startswith("Error:")


# --- parser -------------------------------------------------------------------

def test_parse_action():
    text = "Thought: I should add them\nAction: calculator\nAction Input: 2 + 2"
    parsed = lab.parse_react_output(text)
    assert parsed["type"] == "action"
    assert parsed["action"] == "calculator"
    assert parsed["action_input"] == "2 + 2"
    assert "add" in parsed["thought"]


def test_parse_final():
    parsed = lab.parse_react_output("Thought: done\nFinal Answer: 144")
    assert parsed["type"] == "final"
    assert parsed["answer"] == "144"


def test_parse_incomplete():
    assert lab.parse_react_output("just rambling, no format")["type"] == "incomplete"


# --- execute_action -----------------------------------------------------------

def test_execute_unknown_tool_reports_error():
    out = lab.execute_action("search", "cats")
    assert "unknown tool" in out


# --- the loop -----------------------------------------------------------------

def test_run_agent_uses_tool_then_answers():
    # Script a 2-step run: one calculator action, then a final answer.
    llm = ScriptedLLM(
        [
            "Thought: multiply\nAction: calculator\nAction Input: 4 * 3",
            "Thought: that's the total per month, but the question only needed this\n"
            "Final Answer: 12",
        ]
    )
    result = lab.run_agent("4 members read 3 books each — how many?", llm, tracer=SILENT)
    assert result == "12"
    assert len(llm.calls) == 2
    # The second prompt must contain the observation we computed (12), proving the
    # tool result was fed back into the loop.
    assert "Observation: 12" in llm.calls[1]["messages"][0]["content"]
    # And the loop must have requested the stop sequence.
    assert llm.calls[0]["stop"] == ["Observation:"]


def test_run_agent_respects_step_limit():
    # Every step is an action (never a final answer); the loop must stop at max_steps.
    actions = ["Thought: again\nAction: calculator\nAction Input: 1 + 1"] * 3
    llm = ScriptedLLM(actions)
    result = lab.run_agent("loops forever", llm, tracer=SILENT, max_steps=3)
    assert "Stopped after 3 steps" in result
    assert len(llm.calls) == 3
