"""Tests for core.state module."""


from core.state import State


def test_state_empty(tmp_path):
    state = State(tmp_path)
    assert not state.is_installed("foo")
    assert state.list_installed() == {}


def test_state_record_and_check(tmp_path):
    state = State(tmp_path)
    state.record("git", version="2.40", method="apt")
    assert state.is_installed("git")
    info = state.get("git")
    assert info["version"] == "2.40"
    assert info["method"] == "apt"
    assert "installed_at" in info


def test_state_persistence(tmp_path):
    s1 = State(tmp_path)
    s1.record("docker", version="24.0")
    s2 = State(tmp_path)
    assert s2.is_installed("docker")


def test_state_remove(tmp_path):
    state = State(tmp_path)
    state.record("git", version="2.40")
    assert state.is_installed("git")
    state.remove("git")
    assert not state.is_installed("git")
