"""Offline tests for Lab 2.01 — structured output + repair loop."""

import importlib.util
import sys
from pathlib import Path

import pytest

from shared.testing import ScriptedLLM
from shared import Tracer

_LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_spec = importlib.util.spec_from_file_location("lab2_01", _LAB_PATH)
lab = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lab
_spec.loader.exec_module(lab)

SILENT = Tracer(enabled=False)


# --- extract_json -------------------------------------------------------------

def test_extract_plain():
    assert lab.extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_with_prose_and_fences():
    text = 'Sure! Here you go:\n```json\n{"a": 1, "b": [2, 3]}\n```\nHope that helps.'
    assert lab.extract_json(text) == '{"a": 1, "b": [2, 3]}'


def test_extract_nested_braces():
    assert lab.extract_json('prefix {"x": {"y": 1}} suffix') == '{"x": {"y": 1}}'


def test_extract_none_when_absent():
    assert lab.extract_json("no json here") is None


# --- validate -----------------------------------------------------------------

def test_validate_ok():
    schema = {"name": str, "age": int}
    assert lab.validate({"name": "Ada", "age": 36}, schema) == []


def test_validate_missing_and_wrong_type():
    schema = {"name": str, "age": int}
    errors = lab.validate({"age": "old"}, schema)
    assert any("missing field 'name'" in e for e in errors)
    assert any("'age'" in e and "integer" in e for e in errors)


def test_validate_non_object():
    assert lab.validate([1, 2, 3], {"a": int}) == ["top-level value must be a JSON object"]


# --- get_structured (the repair loop) ----------------------------------------

def test_repair_loop_recovers_on_second_attempt():
    schema = {"name": str, "age": int}
    llm = ScriptedLLM(
        [
            'Sure: {"name": "Ada"}',                 # invalid: missing age
            '{"name": "Ada", "age": 36}',            # fixed
        ]
    )
    result = lab.get_structured(llm, "extract", schema, tracer=SILENT)
    assert result == {"name": "Ada", "age": 36}
    assert len(llm.calls) == 2
    # The second prompt must contain the feedback about the missing field.
    assert "age" in llm.calls[1]["messages"][0]["content"]
    assert "previous response had these problems" in llm.calls[1]["messages"][0]["content"]


def test_raises_after_exhausting_retries():
    schema = {"name": str}
    llm = ScriptedLLM(["nope", "still nope", "nope again"])  # 1 initial + 2 retries
    with pytest.raises(ValueError):
        lab.get_structured(llm, "extract", schema, max_retries=2, tracer=SILENT)
    assert len(llm.calls) == 3
