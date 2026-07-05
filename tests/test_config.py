"""Tests for core.config module."""



from core.config import _deep_merge, load_config, load_yaml


def test_deep_merge_simple():
    base = {"a": 1, "b": 2}
    override = {"b": 3, "c": 4}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": 3, "c": 4}


def test_deep_merge_nested():
    base = {"x": {"a": 1, "b": 2}}
    override = {"x": {"b": 3, "c": 4}}
    result = _deep_merge(base, override)
    assert result == {"x": {"a": 1, "b": 3, "c": 4}}


def test_load_yaml_missing_file(tmp_path):
    result = load_yaml(tmp_path / "nonexistent.yaml")
    assert result == {}


def test_load_yaml_valid(tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text("key: value\nnested:\n  a: 1\n")
    result = load_yaml(f)
    assert result == {"key": "value", "nested": {"a": 1}}


def test_load_config_default_only(tmp_path):
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    (configs_dir / "default.yaml").write_text("env: test\n")
    result = load_config(tmp_path)
    assert result == {"env": "test"}


def test_load_config_with_profile(tmp_path):
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (configs_dir / "default.yaml").write_text("a: 1\nb: 2\n")
    (profiles_dir / "test.yaml").write_text("b: 3\nc: 4\n")
    result = load_config(tmp_path, profile="test")
    assert result == {"a": 1, "b": 3, "c": 4}
