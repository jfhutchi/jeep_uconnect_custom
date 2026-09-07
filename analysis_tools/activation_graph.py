"""Deterministic static activation graph with explicit evidence boundaries."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from analysis_tools.evidence_model import ACTIVATION_STATES, validate_activation_ladder


ROOT_CATEGORIES = (
    "xlet_lifecycle",
    "ui_callback",
    "service_callback",
    "configuration",
    "registration",
    "factory_provider",
    "feature_flag",
    "thread_runnable",
    "test_framework",
    "unknown_external_entry",
)


@dataclass(frozen=True)
class MethodNode:
    id: str
    class_name: str
    method_name: str
    descriptor: str
    root_categories: tuple[str, ...] = ()
    sources: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class CallEdge:
    caller: str
    callee: str
    kind: str
    resolved: bool
    source: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class PathRecord:
    nodes: tuple[str, ...]
    edge_kinds: tuple[str, ...]
    root_categories: tuple[str, ...]


class ActivationGraph:
    def __init__(self, nodes: Iterable[MethodNode], edges: Iterable[CallEdge]):
        node_tuple = tuple(nodes)
        self.nodes = {node.id: node for node in node_tuple}
        if len(self.nodes) != len(node_tuple):
            raise ValueError("duplicate method node id")
        for node in self.nodes.values():
            unknown_roots = sorted(set(node.root_categories) - set(ROOT_CATEGORIES))
            if unknown_roots:
                raise ValueError(f"unknown root categories on {node.id}: {unknown_roots}")
        self.edges = tuple(sorted(
            edges,
            key=lambda edge: (edge.caller, edge.callee, edge.kind, not edge.resolved),
        ))
        for edge in self.edges:
            if edge.caller not in self.nodes:
                raise ValueError(f"unknown edge caller: {edge.caller}")
            if edge.resolved and edge.callee not in self.nodes:
                raise ValueError(f"unknown edge callee: {edge.callee}")
        self._forward = {identifier: [] for identifier in self.nodes}
        self._reverse = {identifier: [] for identifier in self.nodes}
        for edge in self.edges:
            if not edge.resolved or edge.callee not in self.nodes:
                continue
            self._forward[edge.caller].append(edge)
            self._reverse[edge.callee].append(edge)
        for values in self._forward.values():
            values.sort(key=lambda edge: (edge.callee, edge.kind))
        for values in self._reverse.values():
            values.sort(key=lambda edge: (edge.caller, edge.kind))

    @classmethod
    def from_iterables(
        cls, nodes: Iterable[MethodNode], edges: Iterable[CallEdge],
    ) -> "ActivationGraph":
        node_tuple = tuple(nodes)
        if len({node.id for node in node_tuple}) != len(node_tuple):
            raise ValueError("duplicate method node id")
        return cls(node_tuple, tuple(edges))

    def reverse_paths(
        self,
        target: str,
        *,
        max_depth: int = 16,
        max_paths: int = 100,
        excluded_root_categories: tuple[str, ...] = (),
    ) -> list[PathRecord]:
        if target not in self.nodes:
            raise ValueError(f"unknown target: {target}")
        if not 0 < max_depth <= 32:
            raise ValueError("max_depth must be between 1 and 32")
        if not 0 < max_paths <= 100:
            raise ValueError("max_paths must be between 1 and 100")
        excluded = set(excluded_root_categories)
        unknown = excluded - set(ROOT_CATEGORIES)
        if unknown:
            raise ValueError(f"unknown excluded root categories: {sorted(unknown)}")

        queue = deque([(target, (target,), ())])
        found: dict[tuple[str, ...], PathRecord] = {}
        while queue:
            current, reverse_nodes, reverse_kinds = queue.popleft()
            node = self.nodes[current]
            categories = tuple(
                category for category in node.root_categories if category not in excluded
            )
            if categories:
                forward_nodes = tuple(reversed(reverse_nodes))
                found[forward_nodes] = PathRecord(
                    forward_nodes, tuple(reversed(reverse_kinds)), categories,
                )
                if len(found) >= max_paths:
                    break
            if len(reverse_nodes) >= max_depth:
                continue
            for edge in self._reverse[current]:
                if edge.caller in reverse_nodes:
                    continue
                queue.append((
                    edge.caller,
                    reverse_nodes + (edge.caller,),
                    reverse_kinds + (edge.kind,),
                ))
        return sorted(
            found.values(),
            key=lambda path: (len(path.nodes), path.nodes, path.edge_kinds),
        )

    def strong_components(self) -> list[tuple[str, ...]]:
        """Return recursive resolved-call components in stable order."""
        index = 0
        indices: dict[str, int] = {}
        lowlinks: dict[str, int] = {}
        stack: list[str] = []
        on_stack: set[str] = set()
        components: list[tuple[str, ...]] = []

        def visit(identifier: str) -> None:
            nonlocal index
            indices[identifier] = index
            lowlinks[identifier] = index
            index += 1
            stack.append(identifier)
            on_stack.add(identifier)
            for edge in self._forward[identifier]:
                target = edge.callee
                if target not in indices:
                    visit(target)
                    lowlinks[identifier] = min(lowlinks[identifier], lowlinks[target])
                elif target in on_stack:
                    lowlinks[identifier] = min(lowlinks[identifier], indices[target])
            if lowlinks[identifier] != indices[identifier]:
                return
            component = []
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.append(item)
                if item == identifier:
                    break
            component_tuple = tuple(sorted(component))
            has_self_loop = any(
                edge.caller == identifier and edge.callee == identifier
                for edge in self._forward[identifier]
            )
            if len(component_tuple) > 1 or has_self_loop:
                components.append(component_tuple)

        for identifier in sorted(self.nodes):
            if identifier not in indices:
                visit(identifier)
        return sorted(components)

    def activation_ladder(
        self,
        class_name: str,
        *,
        excluded_root_categories: tuple[str, ...] = (),
        state_evidence: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> dict[str, dict[str, Any]]:
        matching = sorted(
            (node for node in self.nodes.values() if node.class_name == class_name),
            key=lambda node: node.id,
        )
        ladder = {
            state: {"classification": "UNKNOWN", "evidence": []}
            for state in ACTIVATION_STATES
        }
        if matching:
            sources = []
            for node in matching:
                for source in node.sources:
                    normalized = dict(source)
                    if normalized not in sources:
                        sources.append(normalized)
            ladder["class_exists"] = {
                "classification": "PROVED",
                "evidence": sources,
            }
            paths = []
            for node in matching:
                paths.extend(self.reverse_paths(
                    node.id,
                    excluded_root_categories=excluded_root_categories,
                ))
            if paths:
                unique_paths = sorted({path.nodes for path in paths})
                ladder["statically_reachable"] = {
                    "classification": "PROVED",
                    "evidence": [list(path) for path in unique_paths],
                }
        if state_evidence is not None:
            unknown_states = set(state_evidence) - set(ACTIVATION_STATES)
            if unknown_states:
                raise ValueError(f"unknown activation states: {sorted(unknown_states)}")
            for state, judgment in state_evidence.items():
                ladder[state] = {
                    "classification": judgment.get("classification"),
                    "evidence": list(judgment.get("evidence", [])),
                }
        validate_activation_ladder(ladder)
        return ladder
