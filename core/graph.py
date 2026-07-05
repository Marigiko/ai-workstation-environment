"""Dependency graph resolution via topological sort."""

from typing import Any


class CircularDependencyError(Exception):
    pass


def resolve(components: list[dict[str, Any]]) -> list[str]:
    """Topological sort of components by their depends_on field.

    Each component dict must have 'name' (str) and 'depends_on' (list[str]).
    Returns ordered list of component names (dependencies first).
    """
    graph: dict[str, list[str]] = {}
    all_names: set[str] = set()

    for comp in components:
        name = comp["name"]
        deps = comp.get("depends_on", [])
        graph[name] = deps
        all_names.add(name)

    visited: set[str] = set()
    in_stack: set[str] = set()
    order: list[str] = []

    def visit(name: str) -> None:
        if name in in_stack:
            raise CircularDependencyError(f"Circular dependency involving: {name}")
        if name in visited:
            return
        in_stack.add(name)
        for dep in graph.get(name, []):
            if dep in all_names:
                visit(dep)
        in_stack.remove(name)
        visited.add(name)
        order.append(name)

    for name in graph:
        visit(name)

    return order
