"""Tests for core.dotfiles module."""

import sys

import pytest

from core.dotfiles import apply_dotfiles, load_manifest


def test_load_manifest_missing(tmp_path):
    result = load_manifest(tmp_path)
    assert result == []


def test_load_manifest_valid(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("links:\n  - src: zsh/.zshrc\n    dst: .zshrc\n")
    result = load_manifest(tmp_path)
    assert len(result) == 1
    assert result[0]["src"] == "zsh/.zshrc"


_skip_win = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlinks require elevated privileges on Windows",
)


@_skip_win
def test_apply_dotfiles_creates_symlink(tmp_path):
    dotfiles_dir = tmp_path / "dotfiles"
    dotfiles_dir.mkdir()
    home = tmp_path / "home"
    home.mkdir()

    src_dir = dotfiles_dir / "zsh"
    src_dir.mkdir()
    (src_dir / ".zshrc").write_text("# zshrc")

    manifest = dotfiles_dir / "manifest.yaml"
    manifest.write_text("links:\n  - src: zsh/.zshrc\n    dst: .zshrc\n")

    created, skipped, errors = apply_dotfiles(dotfiles_dir, home)
    assert created == 1
    assert skipped == 0
    assert errors == 0
    assert (home / ".zshrc").is_symlink()


@_skip_win
def test_apply_dotfiles_skips_existing_correct_link(tmp_path):
    dotfiles_dir = tmp_path / "dotfiles"
    dotfiles_dir.mkdir()
    home = tmp_path / "home"
    home.mkdir()

    src_dir = dotfiles_dir / "zsh"
    src_dir.mkdir()
    (src_dir / ".zshrc").write_text("# zshrc")

    (home / ".zshrc").symlink_to(src_dir / ".zshrc")

    manifest = dotfiles_dir / "manifest.yaml"
    manifest.write_text("links:\n  - src: zsh/.zshrc\n    dst: .zshrc\n")

    created, skipped, errors = apply_dotfiles(dotfiles_dir, home)
    assert created == 0
    assert skipped == 1
    assert errors == 0
