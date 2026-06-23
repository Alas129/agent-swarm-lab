"""Offline tests for Lab 03 — tools + registry + loop."""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM
from shared import Tracer

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab03", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab  # required for @dataclass annotation resolution
_spec.loader.exec_module(lab)

SILENT = Tracer(enabled=False)


# --- tools --------------------------------------------------------------------

def test_calculator():
    assert lab.calculator("3 * (4 + 5)") == "27"


def test_search_hit_and_miss():
    assert "Phobos" in lab.search("tell me about Mars")
    assert lab.search("unknown topic") == "No results found."


def test_word_count():
    assert lab.word_count("one two three") == "3"


# --- Tool.run error handling --------------------------------------------------

def test_tool_run_catches_exceptions():
    boom = lab.Tool("boom", "always fails", lambda _: (_ for _ in ()).throw(ValueError("nope")))
    out = boom.run("x")
    assert out.startswith("Error: tool 'boom' failed")


# --- registry -----------------------------------------------------------------

def test_registry_register_and_run():
    reg = lab.default_registry()
    assert set(reg.names()) == {"calculator", "search", "word_count"}
    assert reg.run("calculator", "2 + 2") == "4"


def test_registry_unknown_tool_lists_available():
    reg = lab.default_registry()
    out = reg.run("weather", "Tokyo")
    assert "unknown tool 'weather'" in out
    assert "calculator" in out  # available tools are listed to aid recovery


def test_build_system_prompt_lists_tools():
    prompt = lab.build_system_prompt(lab.default_registry())
    for name in ("calculator", "search", "word_count"):
        assert name in prompt


# --- loop ---------------------------------------------------------------------

def test_run_agent_multi_tool_flow():
    # search -> word_count -> calculator -> final
    llm = ScriptedLLM(
        [
            "Thought: look it up\nAction: search\nAction Input: Mars",
            "Thought: count words\nAction: word_count\nAction Input: Mars has two moons: Phobos and Deimos.",
            "Thought: multiply\nAction: calculator\nAction Input: 6 * 10",
            "Thought: done\nFinal Answer: 6 words, times 10 is 60.",
        ]
    )
    result = lab.run_agent("...", llm, lab.default_registry(), tracer=SILENT)
    assert result == "6 words, times 10 is 60."
    # The first real observation (the Mars fact) must appear in the second prompt.
    assert "Phobos" in llm.calls[1]["messages"][0]["content"]


def test_run_agent_recovers_from_unknown_tool():
    llm = ScriptedLLM(
        [
            "Thought: try weather\nAction: weather\nAction Input: Tokyo",
            "Thought: oops, use a real tool\nFinal Answer: I cannot get the weather.",
        ]
    )
    result = lab.run_agent("weather?", llm, lab.default_registry(), tracer=SILENT)
    assert "cannot" in result.lower()
    assert "unknown tool 'weather'" in llm.calls[1]["messages"][0]["content"]
