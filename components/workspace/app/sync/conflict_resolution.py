from typing import List, Tuple
from app.schemas.session import MessageCreate, MessageResponse


def resolve_conflict(local: list[dict], remote: list[dict]) -> list[dict]:
    merged = {}
    for msg in local:
        seq = msg.get("sequence", 0)
        merged[seq] = msg
    for msg in remote:
        seq = msg.get("sequence", 0)
        if seq not in merged:
            merged[seq] = msg
        elif msg.get("created_at", "") > merged[seq].get("created_at", ""):
            merged[seq] = msg

    return sorted(merged.values(), key=lambda x: x.get("sequence", 0))


def last_write_wins(local: dict, remote: dict, field: str) -> dict:
    local_time = local.get("updated_at", "")
    remote_time = remote.get("updated_at", "")
    if remote_time > local_time:
        return remote
    return local
