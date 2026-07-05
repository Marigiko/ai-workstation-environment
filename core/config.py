"""YAML configuration loader with layered merge."""

from pathlib import Path
from typing import Any

import yaml

from core.logger import log


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_config(
    project_root: Path,
    profile: str | None = None,
) -> dict[str, Any]:
    layers: list[dict] = []

    default_path = project_root / "configs" / "default.yaml"
    layers.append(load_yaml(default_path))

    if profile:
        profile_path = project_root / "profiles" / f"{profile}.yaml"
        if profile_path.exists():
            layers.append(load_yaml(profile_path))
        else:
            log.warning("Profile not found: %s", profile_path)

    local_path = project_root / "configs" / "local.yaml"
    layers.append(load_yaml(local_path))

    merged: dict = {}
    for layer in layers:
        merged = _deep_merge(merged, layer)

    return merged
