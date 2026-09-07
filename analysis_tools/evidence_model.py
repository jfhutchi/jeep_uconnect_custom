"""Evidence vocabulary and deterministic metadata-only JSON output.

The helpers in this module never read recovered artifacts.  They validate the
claim boundary used by the read-only analyzers and reject host-specific paths
before generated evidence is committed.
"""

from __future__ import annotations

import json
import ntpath
import os
import posixpath
from pathlib import Path
import tempfile
from typing import Any, Mapping


CLASSIFICATIONS = ("PROVED", "STRONGLY INFERRED", "UNKNOWN")

ACTIVATION_STATES = (
    "class_exists",
    "statically_reachable",
    "activation_mechanism_exists",
    "activation_configured",
    "production_enabled",
    "listener_executable",
    "externally_reachable",
)

DIRECT_SOURCE_KINDS = frozenset(
    {
        "parsed_structure",
        "bytecode_edge",
        "resource_structure",
        "artifact_hash",
        "native_call_edge",
    }
)


def validate_evidence(record: Mapping[str, Any]) -> None:
    """Validate one classified claim without promoting inferential evidence."""
    classification = record.get("classification")
    if classification not in CLASSIFICATIONS:
        raise ValueError(f"invalid evidence classification: {classification!r}")
    claim = record.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("evidence claim must be a nonempty string")
    sources = record.get("sources")
    if not isinstance(sources, list):
        raise ValueError("evidence sources must be a list")
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("evidence source must be an object")
        if not isinstance(source.get("kind"), str):
            raise ValueError("evidence source requires a kind")
        if not isinstance(source.get("artifact"), str):
            raise ValueError("evidence source requires an artifact")
    if classification == "PROVED":
        if not sources:
            raise ValueError("PROVED claim requires a source")
        if not any(source.get("kind") in DIRECT_SOURCE_KINDS for source in sources):
            raise ValueError("PROVED claim requires a direct source")


def validate_activation_ladder(ladder: Mapping[str, Any]) -> None:
    """Require an independent judgment for every locked activation state."""
    if set(ladder) != set(ACTIVATION_STATES):
        missing = sorted(set(ACTIVATION_STATES) - set(ladder))
        extra = sorted(set(ladder) - set(ACTIVATION_STATES))
        raise ValueError(f"activation states mismatch: missing={missing}, extra={extra}")
    for state in ACTIVATION_STATES:
        judgment = ladder[state]
        if not isinstance(judgment, Mapping):
            raise ValueError(f"activation state {state} must be an object")
        if judgment.get("classification") not in CLASSIFICATIONS:
            raise ValueError(f"activation state {state} has invalid classification")
        if not isinstance(judgment.get("evidence"), list):
            raise ValueError(f"activation state {state} requires an evidence list")


def _is_absolute_path(value: str) -> bool:
    if "://" in value:
        return False
    return ntpath.isabs(value) or posixpath.isabs(value)


def _reject_absolute_paths(value: Any, location: str = "$") -> None:
    if isinstance(value, str):
        if _is_absolute_path(value):
            raise ValueError(f"absolute path at {location}: {value!r}")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_absolute_paths(item, f"{location}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_absolute_paths(item, f"{location}[{index}]")


def _record_sort_key(value: Mapping[str, Any]) -> tuple[Any, ...]:
    rank = value.get("rank")
    rank_key = rank if isinstance(rank, int) else 2**31
    return (
        rank_key,
        str(value.get("artifact", "")),
        str(value.get("member", "")),
        int(value.get("offset", -1)) if isinstance(value.get("offset", -1), int) else -1,
        str(value.get("id", "")),
        str(value.get("category", "")),
        str(value.get("name", "")),
        json.dumps(value, sort_keys=True, separators=(",", ":")),
    )


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        normalized = [_normalize(item) for item in value]
        if normalized and all(isinstance(item, Mapping) for item in normalized):
            normalized.sort(key=_record_sort_key)
        return normalized
    return value


def json_bytes(value: Any) -> bytes:
    """Return canonical UTF-8 JSON after enforcing path and type boundaries."""
    _reject_absolute_paths(value)
    normalized = _normalize(value)
    try:
        text = json.dumps(normalized, indent=2, sort_keys=True, ensure_ascii=True)
    except (TypeError, ValueError) as error:
        raise ValueError(f"value is not JSON serializable: {error}") from error
    return (text + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    """Atomically replace *path* with canonical metadata-only JSON."""
    data = json_bytes(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
