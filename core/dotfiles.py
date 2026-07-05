"""Dotfiles management: manifest-driven symlink engine."""

from pathlib import Path

import yaml

from core.logger import log


def load_manifest(dotfiles_dir: Path) -> list[dict]:
    manifest_path = dotfiles_dir / "manifest.yaml"
    if not manifest_path.exists():
        return []
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    return data.get("links", []) if data else []


def apply_dotfiles(
    dotfiles_dir: Path,
    home: Path,
    force: bool = False,
) -> tuple[int, int, int]:
    """Apply dotfile symlinks. Returns (created, skipped, errors)."""
    links = load_manifest(dotfiles_dir)
    created = skipped = errors = 0

    for entry in links:
        src_rel = entry.get("src", "")
        dst_rel = entry.get("dst", "")
        if not src_rel or not dst_rel:
            log.warning("Skipping invalid manifest entry: %s", entry)
            errors += 1
            continue

        src = dotfiles_dir / src_rel
        dst = home / dst_rel

        if not src.exists():
            log.warning("Source not found: %s", src)
            errors += 1
            continue

        if dst.is_symlink():
            if dst.resolve() == src.resolve():
                skipped += 1
                continue
            if not force:
                log.warning("Symlink exists, different target: %s -> %s", dst, dst.resolve())
                errors += 1
                continue
            dst.unlink()

        if dst.exists():
            if not force:
                log.warning("Target exists (not a symlink): %s", dst)
                errors += 1
                continue
            backup = dst.with_suffix(dst.suffix + ".bak")
            log.info("Backing up %s -> %s", dst, backup)
            dst.rename(backup)

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
        log.info("Linked: %s -> %s", dst, src)
        created += 1

    return created, skipped, errors
