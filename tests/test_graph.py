"""Tests for core.graph module."""

import pytest

from core.graph import CircularDependencyError, resolve


def test_resolve_empty():
    assert resolve([]) == []


def test_resolve_no_deps():
    components = [
        {"name": "a", "depends_on": []},
        {"name": "b", "depends_on": []},
    ]
    result = resolve(components)
    assert set(result) == {"a", "b"}


def test_resolve_with_deps():
    components = [
        {"name": "c", "depends_on": ["a", "b"]},
        {"name": "b", "depends_on": ["a"]},
        {"name": "a", "depends_on": []},
    ]
    result = resolve(components)
    assert result.index("a") < result.index("b")
    assert result.index("a") < result.index("c")
    assert result.index("b") < result.index("c")


def test_resolve_circular_raises():
    components = [
        {"name": "a", "depends_on": ["b"]},
        {"name": "b", "depends_on": ["a"]},
    ]
    with pytest.raises(CircularDependencyError):
        resolve(components)


def test_resolve_chain():
    components = [
        {"name": "d", "depends_on": ["c"]},
        {"name": "c", "depends_on": ["b"]},
        {"name": "b", "depends_on": ["a"]},
        {"name": "a", "depends_on": []},
    ]
    result = resolve(components)
    assert result == ["a", "b", "c", "d"]
