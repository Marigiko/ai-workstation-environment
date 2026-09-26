"""Tests for detect_projects_dir (P2.6)."""

from pathlib import Path

from core.detect import detect_projects_dir

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_detect_projects_dir_from_env(monkeypatch):
    monkeypatch.setenv("AWE_PROJECTS_DIR", "/tmp/custom-projects")
    assert detect_projects_dir() == "/tmp/custom-projects"


def test_detect_projects_dir_defaults_to_repo_parent(monkeypatch):
    monkeypatch.delenv("AWE_PROJECTS_DIR", raising=False)
    assert Path(detect_projects_dir()) == REPO_ROOT.parent
