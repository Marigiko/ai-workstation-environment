from typing import List, Tuple
from datetime import datetime


class VectorClock:
    def __init__(self, clock: dict[str, int] = None):
        self.clock = clock or {}

    def increment(self, node: str):
        self.clock[node] = self.clock.get(node, 0) + 1

    def merge(self, other: "VectorClock"):
        for node, count in other.clock.items():
            self.clock[node] = max(self.clock.get(node, 0), count)

    def compare(self, other: "VectorClock") -> str:
        self_greater = any(self.clock.get(n, 0) > other.clock.get(n, 0) for n in self.clock)
        other_greater = any(other.clock.get(n, 0) > self.clock.get(n, 0) for n in other.clock)

        if self_greater and not other_greater:
            return "after"
        elif other_greater and not self_greater:
            return "before"
        elif not self_greater and not other_greater:
            return "concurrent"
        return "equal"

    def to_dict(self) -> dict:
        return self.clock.copy()

    @classmethod
    def from_dict(cls, data: dict) -> "VectorClock":
        return cls(data.copy())
