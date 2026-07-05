"""Tests for core.detect module."""

from core.detect import detect_os, detect_package_manager, detect_shell, detect_wsl


def test_detect_os_returns_string():
    result = detect_os()
    assert isinstance(result, str)
    assert result in ("linux", "darwin", "windows")


def test_detect_wsl_returns_tuple():
    is_wsl, version = detect_wsl()
    assert isinstance(is_wsl, bool)
    assert isinstance(version, int)
    assert version in (0, 1, 2)


def test_detect_shell_returns_string():
    result = detect_shell()
    assert isinstance(result, str)
    assert len(result) > 0


def test_detect_package_manager_returns_string():
    result = detect_package_manager()
    assert isinstance(result, str)
