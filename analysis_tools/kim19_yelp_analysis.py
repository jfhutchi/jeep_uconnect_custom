"""Deterministic, read-only reconstruction of the recovered KIM19 Yelp Xlet.

The analyzer parses class and resource bytes without loading vendor classes. It
validates reviewed claims against exact JVM instructions and emits only derived,
source-bound JSON. It never opens a network connection or writes recovered input.
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any
import zipfile

from analysis_tools.java_classfile import ClassModel, parse_class


LABELS = {
    "PROVED",
    "STRONGLY SUPPORTED",
    "INFERRED",
    "UNKNOWN",
    "TARGET OBSERVATION REQUIRED",
}
REPORT_NAMES = (
    "launch_graph",
    "runtime_gates",
    "input_dataflow",
    "network_fields",
    "response_actions",
    "failure_paths",
    "stock_handoffs",
)
NOTES_PATH = Path(__file__).with_name("kim19_yelp_notes.json")
_ALLOWED_STATIC_OUTPUTS = {"original_checkout_snapshot.json"}
_CREDENTIAL_PATTERN = re.compile(
    r"\b(?:basic|bearer)\s+[A-Za-z0-9+/_.=-]{4,}|"
    r"\b(?:oauth_consumer_secret|api[_-]?key|password)\s*[=:]\s*\S+",
    re.IGNORECASE,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")


def _safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("source path must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe source path: {value!r}")
    return path


def _read_checked(root: Path, record: dict[str, Any]) -> tuple[Path, bytes]:
    path = _safe_relative_path(record.get("path"))
    candidate = root.joinpath(*path.parts)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as error:
        raise ValueError(f"missing source: {path.as_posix()}") from error
    root_resolved = root.resolve(strict=True)
    if root_resolved != resolved and root_resolved not in resolved.parents:
        raise ValueError(f"source escapes work root: {path.as_posix()}")
    if candidate.is_symlink() or not resolved.is_file():
        raise ValueError(f"source is not a regular file: {path.as_posix()}")
    data = resolved.read_bytes()
    if len(data) != record.get("size"):
        raise ValueError(f"source size mismatch: {path.as_posix()}")
    if digest(data) != record.get("sha256"):
        raise ValueError(f"source hash mismatch: {path.as_posix()}")
    return resolved, data


@dataclass
class SourceSet:
    root: Path
    paths: dict[str, Path]
    records: dict[str, dict[str, Any]]
    raw: dict[str, bytes]
    jar_members: dict[str, bytes]
    classes: dict[str, ClassModel]

    def assert_unchanged(self) -> None:
        for name, path in self.paths.items():
            data = path.read_bytes()
            record = self.records[name]
            if len(data) != record["size"] or digest(data) != record["sha256"]:
                raise ValueError(f"source changed during analysis: {record['path']}")


def _load_jar(data: bytes) -> tuple[dict[str, bytes], dict[str, ClassModel]]:
    from io import BytesIO

    members: dict[str, bytes] = {}
    classes: dict[str, ClassModel] = {}
    with zipfile.ZipFile(BytesIO(data)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("duplicate Yelp JAR member")
        total = 0
        for info in infos:
            path = _safe_relative_path(info.filename.rstrip("/")) if not info.is_dir() else None
            if info.is_dir():
                continue
            if path is None or info.file_size > 8 * 1024 * 1024:
                raise ValueError("invalid or oversized Yelp JAR member")
            total += info.file_size
            if total > 256 * 1024 * 1024:
                raise ValueError("Yelp JAR uncompressed size limit exceeded")
            payload = archive.read(info)
            name = path.as_posix()
            members[name] = payload
            if name.endswith(".class"):
                model = parse_class(payload)
                if model.name in classes:
                    raise ValueError(f"duplicate parsed class: {model.name}")
                if name != model.name + ".class":
                    raise ValueError(f"class/member name mismatch: {name}")
                classes[model.name] = model
    return members, classes


def load_sources(work: Path, notes: dict[str, Any]) -> SourceSet:
    if not work.exists() or not work.is_dir():
        raise ValueError("recovered work root is not a directory")
    records = notes.get("sources")
    if not isinstance(records, dict) or set(records) != {"descriptor", "key_jar", "yelp_jar"}:
        raise ValueError("notes must declare descriptor, key_jar, and yelp_jar sources")
    paths: dict[str, Path] = {}
    raw: dict[str, bytes] = {}
    for name, record in records.items():
        if not isinstance(record, dict):
            raise ValueError(f"invalid source record: {name}")
        path, data = _read_checked(work, record)
        paths[name] = path
        raw[name] = data
    members, classes = _load_jar(raw["yelp_jar"])
    result = SourceSet(work.resolve(), paths, copy.deepcopy(records), raw, members, classes)
    result.assert_unchanged()
    return result


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _unique_ids(rows: object, description: str) -> None:
    if not isinstance(rows, list):
        raise ValueError(f"{description} must be a list")
    ids = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"{description} records require non-empty string IDs")
        ids.append(row["id"])
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate ID in {description}")


def validate_notes(notes: dict[str, Any]) -> None:
    if not isinstance(notes, dict) or notes.get("format") != "kim19-yelp-reviewed-notes-v1":
        raise ValueError("unsupported Yelp notes format")
    if notes.get("labels") != sorted(LABELS):
        raise ValueError("notes label vocabulary does not match the locked set")
    reports = notes.get("reports")
    if not isinstance(reports, dict) or set(reports) != set(REPORT_NAMES):
        raise ValueError("notes must contain exactly the seven Yelp reports")
    for item in _walk(notes):
        if isinstance(item, dict) and "label" in item and item["label"] not in LABELS:
            raise ValueError(f"unknown evidence label: {item['label']!r}")
        if isinstance(item, str) and _CREDENTIAL_PATTERN.search(item):
            raise ValueError("public notes contain credential-like material")
    graph = reports["launch_graph"]
    if not isinstance(graph, dict) or set(graph) < {"nodes", "edges"}:
        raise ValueError("launch graph requires nodes and edges")
    _unique_ids(graph["nodes"], "launch nodes")
    _unique_ids(graph["edges"], "launch edges")
    node_ids = {row["id"] for row in graph["nodes"]}
    for edge in graph["edges"]:
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            raise ValueError(f"launch edge {edge['id']} references an unknown node")
    list_keys = {
        "runtime_gates": "gates",
        "input_dataflow": "flows",
        "network_fields": "fields",
        "response_actions": "actions",
        "failure_paths": "paths",
        "stock_handoffs": "handoffs",
    }
    for report_name, list_key in list_keys.items():
        report = reports[report_name]
        if not isinstance(report, dict) or list_key not in report:
            raise ValueError(f"{report_name} requires {list_key}")
        _unique_ids(report[list_key], f"{report_name}.{list_key}")


def validate_java_site(site: dict[str, Any], classes: dict[str, ClassModel]) -> dict[str, Any]:
    required = {
        "class", "method", "descriptor", "bci", "opcode", "owner", "name",
        "callee_descriptor",
    }
    if not isinstance(site, dict) or not required <= set(site):
        raise ValueError("Java evidence site is missing identity fields")
    class_name = site["class"]
    if class_name not in classes:
        raise ValueError(f"evidence class not found: {class_name}")
    method = classes[class_name].method(site["method"], site["descriptor"])
    matching_instruction = [row for row in method.instructions if row.offset == site["bci"]]
    if len(matching_instruction) != 1 or matching_instruction[0].mnemonic != site["opcode"]:
        raise ValueError("evidence BCI/opcode does not match parsed method")
    matching_edge = [row for row in method.member_edges if row.offset == site["bci"]]
    if len(matching_edge) != 1:
        raise ValueError("evidence BCI does not identify one member edge")
    edge = matching_edge[0]
    if (edge.owner, edge.name, edge.descriptor, edge.opcode) != (
        site["owner"], site["name"], site["callee_descriptor"], site["opcode"],
    ):
        raise ValueError("evidence callee does not match parsed member edge")
    return copy.deepcopy(site)


def _bind_sites(value: object, sources: SourceSet) -> object:
    if isinstance(value, dict):
        if {"class", "method", "descriptor", "bci"} <= set(value):
            bound = validate_java_site(value, sources.classes)
            bound["source_jar_sha256"] = sources.records["yelp_jar"]["sha256"]
            return bound
        return {key: _bind_sites(child, sources) for key, child in value.items()}
    if isinstance(value, list):
        return [_bind_sites(child, sources) for child in value]
    return value


def _sort_id_lists(value: object) -> object:
    if isinstance(value, dict):
        return {key: _sort_id_lists(child) for key, child in value.items()}
    if isinstance(value, list):
        rendered = [_sort_id_lists(child) for child in value]
        if rendered and all(isinstance(child, dict) and isinstance(child.get("id"), str)
                            for child in rendered):
            return sorted(rendered, key=lambda child: child["id"])
        return rendered
    return value


def build_reports(notes: dict[str, Any], sources: SourceSet) -> dict[str, dict[str, Any]]:
    validate_notes(notes)
    notes_hash = digest(canonical_bytes(notes))
    source_manifest = {
        name: {key: record[key] for key in ("path", "sha256", "size")}
        for name, record in sorted(sources.records.items())
    }
    reports: dict[str, dict[str, Any]] = {}
    for name in REPORT_NAMES:
        body = _sort_id_lists(_bind_sites(copy.deepcopy(notes["reports"][name]), sources))
        assert isinstance(body, dict)
        reports[name] = {
            "app": copy.deepcopy(notes["app"]),
            "evidence_labels": sorted(LABELS),
            "format": "kim19-yelp-analysis-v1",
            "notes_sha256": notes_hash,
            "report": name,
            "runtime_boundary": (
                "Static recovered-artifact analysis; current target state and backend availability "
                "are not inferred."
            ),
            "sources": source_manifest,
            **body,
        }
    sources.assert_unchanged()
    return reports


def write_outputs(reports: dict[str, dict[str, Any]], output: Path) -> None:
    if set(reports) != set(REPORT_NAMES):
        raise ValueError("writer requires exactly the seven Yelp reports")
    output.mkdir(parents=True, exist_ok=True)
    for name in REPORT_NAMES:
        (output / f"{name}.json").write_bytes(canonical_bytes(reports[name]))


def verify_outputs(reports: dict[str, dict[str, Any]], output: Path) -> None:
    if not output.exists() or not output.is_dir():
        raise ValueError("report output directory is missing")
    expected = {f"{name}.json" for name in REPORT_NAMES}
    actual = {path.name for path in output.glob("*.json")}
    unexpected = actual - expected - _ALLOWED_STATIC_OUTPUTS
    if unexpected:
        raise ValueError(f"unexpected report file: {sorted(unexpected)[0]}")
    missing = expected - actual
    if missing:
        raise ValueError(f"missing report file: {sorted(missing)[0]}")
    for name in REPORT_NAMES:
        path = output / f"{name}.json"
        if path.read_bytes() != canonical_bytes(reports[name]):
            raise ValueError(f"stale report: {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="Recovered work root (read-only)")
    parser.add_argument("--output", type=Path, required=True, help="Directory for seven JSON reports")
    parser.add_argument("--notes", type=Path, default=NOTES_PATH, help="Reviewed notes JSON")
    parser.add_argument("--javap", default="javap", help="JDK javap executable for independent checks")
    parser.add_argument("--check", action="store_true", help="Verify committed output bytes")
    args = parser.parse_args()
    if not args.notes.is_file():
        parser.error("reviewed notes file is missing")
    notes = json.loads(args.notes.read_text(encoding="utf-8"))
    sources = load_sources(args.work, notes)
    reports = build_reports(notes, sources)
    if args.check:
        verify_outputs(reports, args.output)
    else:
        write_outputs(reports, args.output)
    sources.assert_unchanged()
    print(f"{len(reports)} Yelp reports {'verified' if args.check else 'written'}; recovered sources unchanged")


if __name__ == "__main__":
    main()
