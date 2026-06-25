"""Offline tests for Lab 04 — memory + chat agent."""

import importlib.util
import sys
from pathlib import Path

from shared.testing import ScriptedLLM

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab04", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab  # required for @dataclass annotation resolution
_spec.loader.exec_module(lab)


# --- Memory -------------------------------------------------------------------

def test_memory_accumulates_turns():
    mem = lab.Memory()
    mem.add_user("hi")
    mem.add_assistant("hello")
    assert mem.render() == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_memory_render_returns_a_copy():
    mem = lab.Memory()
    mem.add_user("hi")
    snapshot = mem.render()
    snapshot.append({"role": "user", "content": "mutation"})
    assert len(mem.render()) == 1  # internal state untouched


def test_memory_window_keeps_most_recent():
    mem = lab.Memory(max_messages=2)
    for i in range(4):
        mem.add_user(f"m{i}")
    contents = [m["content"] for m in mem.render()]
    assert contents == ["m2", "m3"]  # oldest dropped


def test_memory_no_window_keeps_everything():
    mem = lab.Memory()
    for i in range(5):
        mem.add_user(f"m{i}")
    assert len(mem.render()) == 5


# --- ChatAgent ----------------------------------------------------------------

def test_chat_agent_resends_history():
    llm = ScriptedLLM(["Nice to meet you, Sam.", "Your name is Sam."])
    agent = lab.ChatAgent(llm)
    agent.send("I'm Sam.")
    agent.send("What's my name?")
    # The SECOND model call must include the full prior conversation (memory at work):
    # user, assistant, user.
    second_call_messages = llm.calls[1]["messages"]
    assert [m["role"] for m in second_call_messages] == ["user", "assistant", "user"]
    assert second_call_messages[0]["content"] == "I'm Sam."


def test_chat_agent_stores_reply():
    llm = ScriptedLLM(["hello there"])
    agent = lab.ChatAgent(llm)
    agent.send("hi")
    assert agent.memory.render()[-1] == {"role": "assistant", "content": "hello there"}


def test_system_prompt_passed_but_not_stored():
    llm = ScriptedLLM(["ok"])
    agent = lab.ChatAgent(llm, system="You are terse.")
    agent.send("hi")
    assert llm.calls[0]["system"] == "You are terse."
    # The system prompt is not part of stored memory.
    assert all("terse" not in m["content"] for m in agent.memory.render())
