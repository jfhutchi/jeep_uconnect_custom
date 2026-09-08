#!/usr/bin/env python3
"""Deterministic Performance Pages export evidence analysis."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from analysis_tools.java_classfile import parse_class


REPORT_FILENAMES = (
    "performance_pages_export_summary.json",
    "performance_pages_export_class_evidence.json",
    "performance_pages_filename_dataflow.json",
    "performance_pages_html_fields.json",
    "performance_pages_export_failure_signatures.json",
)
EVIDENCE_LABELS = [
    "PROVED",
    "INFERRED",
    "TARGET OBSERVATION REQUIRED",
    "UNKNOWN",
]
PROVENANCE_FIELDS = {
    "label",
    "source_ids",
    "evidence_binding_ids",
    "class_function",
    "invocation_dataflow",
    "uncertainty",
}
SOURCE_FIELDS = {"id", "corpus_relative_path", "sha256", "description"}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
DRIVE_PATH_RE = re.compile(r"[A-Za-z]:")
CONTROL_CLASSIFICATIONS = {
    "fixed",
    "platform-controlled",
    "vehicle-controlled",
    "user-controlled",
    "indirectly user-influenced",
    "unknown",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def strict_json_loads(text: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"invalid JSON numeric constant: {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        text,
        parse_constant=reject_constant,
        object_pairs_hook=reject_duplicate_keys,
    )


def _object(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"unknown field {path}.{unknown[0]}")
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"missing field {path}.{missing[0]}")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a nonempty string")
    return value


def _string_list(value: Any, path: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a nonempty list"
        raise ValueError(f"{path} must be {qualifier} of nonempty strings")
    for index, item in enumerate(value):
        _string(item, f"{path}[{index}]")
    return value


def _list(value: Any, path: str, *, allow_empty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a nonempty list"
        raise ValueError(f"{path} must be {qualifier}")
    return value


def _enum(value: Any, choices: set[str], path: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"{path} must be one of {sorted(choices)}")
    return value


def _validate_relative_path(value: Any, path: str) -> str:
    text = _string(value, path)
    candidate = PurePosixPath(text)
    if (
        "\\" in text
        or DRIVE_PATH_RE.match(text)
        or candidate.is_absolute()
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise ValueError(f"{path} must be a safe corpus-relative path")
    return text


def _unique_ids(rows: list[Any], path: str) -> None:
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        row_id = _string(row.get("id"), f"{path}[{index}].id")
        if row_id in seen:
            raise ValueError(f"duplicate {path} id: {row_id}")
        seen.add(row_id)


def _validate_sources(value: Any, path: str) -> set[str]:
    rows = _list(value, path)
    _unique_ids(rows, path)
    source_ids: set[str] = set()
    source_paths: set[str] = set()
    for index, source in enumerate(rows):
        item_path = f"{path}[{index}]"
        _object(source, SOURCE_FIELDS, item_path)
        source_id = _string(source["id"], f"{item_path}.id")
        relative_path = _validate_relative_path(
            source["corpus_relative_path"], f"{item_path}.corpus_relative_path"
        )
        sha256 = source["sha256"]
        if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256):
            raise ValueError(f"{item_path}.sha256 must be a lowercase SHA-256 digest")
        _string(source["description"], f"{item_path}.description")
        if relative_path in source_paths:
            raise ValueError(f"duplicate {path} corpus_relative_path: {relative_path}")
        source_ids.add(source_id)
        source_paths.add(relative_path)
    return source_ids


def _validate_provenance(
    value: Any,
    source_ids: set[str],
    path: str,
    evidence_binding_ids: set[str] | None = None,
) -> None:
    row = _object(value, PROVENANCE_FIELDS, path)
    _enum(row["label"], set(EVIDENCE_LABELS), f"{path}.evidence label")
    references = _string_list(row["source_ids"], f"{path}.source_ids")
    if len(references) != len(set(references)):
        raise ValueError(f"{path}.source_ids contains a duplicate source id")
    for source_id in references:
        if source_id not in source_ids:
            raise ValueError(f"{path} references unknown source id: {source_id}")
    binding_references = _string_list(
        row["evidence_binding_ids"],
        f"{path}.evidence_binding_ids",
        allow_empty=True,
    )
    if len(binding_references) != len(set(binding_references)):
        raise ValueError(f"{path}.evidence_binding_ids contains a duplicate binding id")
    if evidence_binding_ids is not None:
        for binding_id in binding_references:
            if binding_id not in evidence_binding_ids:
                raise ValueError(f"{path} references unknown evidence binding id: {binding_id}")
    _string(row["class_function"], f"{path}.class_function")
    _string_list(row["invocation_dataflow"], f"{path}.invocation_dataflow")
    _string(row["uncertainty"], f"{path}.uncertainty")


def _validate_common(notes: Any, fields: set[str], path: str) -> tuple[dict[str, Any], set[str]]:
    row = _object(notes, fields, path)
    if row["schema_version"] != 1 or isinstance(row["schema_version"], bool):
        raise ValueError(f"{path}.schema_version must be 1")
    _string(row["scope"], f"{path}.scope")
    if row["evidence_labels"] != EVIDENCE_LABELS:
        raise ValueError(f"{path}.evidence_labels must contain the exact evidence labels")
    return row, _validate_sources(row["source_artifacts"], f"{path}.source_artifacts")


def _validate_class_evidence_selections(
    value: Any,
    source_ids: set[str],
    path: str,
) -> set[str]:
    rows = _list(value, path, allow_empty=True)
    _unique_ids(rows, path)
    fields = {
        "id",
        "source_id",
        "class_name",
        "class_sha256",
        "method_name",
        "descriptor",
        "instruction_count",
        "selected_instructions",
    }
    for index, row in enumerate(rows):
        item_path = f"{path}[{index}]"
        _object(row, fields, item_path)
        _string(row["id"], f"{item_path}.id")
        source_id = _string(row["source_id"], f"{item_path}.source_id")
        if source_id not in source_ids:
            raise ValueError(f"{item_path} references unknown source id: {source_id}")
        _string(row["class_name"], f"{item_path}.class_name")
        sha256 = row["class_sha256"]
        if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256):
            raise ValueError(f"{item_path}.class_sha256 must be a lowercase SHA-256 digest")
        _string(row["method_name"], f"{item_path}.method_name")
        descriptor = _string(row["descriptor"], f"{item_path}.descriptor")
        if not descriptor.startswith("("):
            raise ValueError(f"{item_path}.descriptor must be a JVM method descriptor")
        count = row["instruction_count"]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"{item_path}.instruction_count must be a nonnegative integer")
        selections = _list(row["selected_instructions"], f"{item_path}.selected_instructions")
        seen: set[tuple[Any, ...]] = set()
        for instruction_index, instruction in enumerate(selections):
            instruction_path = f"{item_path}.selected_instructions[{instruction_index}]"
            if not isinstance(instruction, dict):
                raise ValueError(f"{instruction_path} must be an object")
            kind = instruction.get("kind")
            if kind == "member":
                expected_fields = {"kind", "bci", "opcode", "owner", "name", "descriptor"}
                _object(instruction, expected_fields, instruction_path)
                for key in ("opcode", "owner", "name", "descriptor"):
                    _string(instruction[key], f"{instruction_path}.{key}")
                identity = (
                    kind,
                    instruction.get("bci"),
                    instruction["opcode"],
                    instruction["owner"],
                    instruction["name"],
                    instruction["descriptor"],
                )
            elif kind == "string":
                expected_fields = {"kind", "bci", "opcode", "value"}
                _object(instruction, expected_fields, instruction_path)
                _string(instruction["opcode"], f"{instruction_path}.opcode")
                _string(instruction["value"], f"{instruction_path}.value")
                identity = (
                    kind,
                    instruction.get("bci"),
                    instruction["opcode"],
                    instruction["value"],
                )
            else:
                raise ValueError(f"{instruction_path}.kind must be member or string")
            bci = instruction["bci"]
            if isinstance(bci, bool) or not isinstance(bci, int) or bci < 0:
                raise ValueError(f"{instruction_path}.bci must be a nonnegative integer")
            if identity in seen:
                raise ValueError(f"duplicate selected instruction in {item_path}")
            seen.add(identity)
    return {row["id"] for row in rows}


def _validate_unresolved_gates(
    value: Any,
    source_ids: set[str],
    evidence_binding_ids: set[str],
    path: str,
) -> None:
    rows = _list(value, path, allow_empty=True)
    _unique_ids(rows, path)
    fields = {"id", "gate", "required_observation", "provenance"}
    for index, row in enumerate(rows):
        item_path = f"{path}[{index}]"
        _object(row, fields, item_path)
        _string(row["id"], f"{item_path}.id")
        _string(row["gate"], f"{item_path}.gate")
        _string(row["required_observation"], f"{item_path}.required_observation")
        _validate_provenance(
            row["provenance"],
            source_ids,
            f"{item_path}.provenance",
            evidence_binding_ids,
        )


def validate_producer_notes(notes: Any) -> dict[str, Any]:
    fields = {
        "schema_version",
        "scope",
        "evidence_labels",
        "source_artifacts",
        "class_evidence_selections",
        "variants",
        "export_reachability",
        "filename_dataflow",
        "html_generation",
        "failure_signatures",
        "unresolved_gates",
    }
    row, source_ids = _validate_common(notes, fields, "producer_notes")
    evidence_binding_ids = _validate_class_evidence_selections(
        row["class_evidence_selections"],
        source_ids,
        "producer_notes.class_evidence_selections",
    )

    variants = _list(row["variants"], "producer_notes.variants")
    _unique_ids(variants, "variants")
    variant_fields = {"id", "display_name", "package_id", "export_role", "provenance"}
    for index, variant in enumerate(variants):
        path = f"producer_notes.variants[{index}]"
        _object(variant, variant_fields, path)
        for key in ("id", "display_name", "package_id", "export_role"):
            _string(variant[key], f"{path}.{key}")
        _validate_provenance(
            variant["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )

    reachability = _object(
        row["export_reachability"],
        {"status", "entry_point", "call_chain", "gates", "provenance"},
        "producer_notes.export_reachability",
    )
    _enum(
        reachability["status"],
        {"statically_reachable", "statically_gated", "not_statically_reachable", "unknown"},
        "producer_notes.export_reachability.status",
    )
    _string(reachability["entry_point"], "producer_notes.export_reachability.entry_point")
    call_chain = _list(reachability["call_chain"], "producer_notes.export_reachability.call_chain")
    for index, step in enumerate(call_chain):
        path = f"producer_notes.export_reachability.call_chain[{index}]"
        _object(step, {"operation", "provenance"}, path)
        _string(step["operation"], f"{path}.operation")
        _validate_provenance(
            step["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )
    gates = _list(
        reachability["gates"], "producer_notes.export_reachability.gates", allow_empty=True
    )
    _unique_ids(gates, "export_reachability.gates")
    for index, gate in enumerate(gates):
        path = f"producer_notes.export_reachability.gates[{index}]"
        _object(gate, {"id", "condition", "effect", "provenance"}, path)
        for key in ("id", "condition", "effect"):
            _string(gate[key], f"{path}.{key}")
        _validate_provenance(
            gate["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )
    _validate_provenance(
        reachability["provenance"],
        source_ids,
        "producer_notes.export_reachability.provenance",
        evidence_binding_ids,
    )

    filename = _object(
        row["filename_dataflow"],
        {
            "classification",
            "destination_source",
            "path_components",
            "sanitization",
            "collision_behavior",
            "overwrite_behavior",
            "provenance",
        },
        "producer_notes.filename_dataflow",
    )
    _enum(
        filename["classification"],
        {"fixed", "system_derived", "partially_user_controlled", "arbitrary_filename", "unknown"},
        "producer_notes.filename_dataflow.classification",
    )
    _string(filename["destination_source"], "producer_notes.filename_dataflow.destination_source")
    components = _list(filename["path_components"], "producer_notes.filename_dataflow.path_components")
    orders: set[int] = set()
    for index, component in enumerate(components):
        path = f"producer_notes.filename_dataflow.path_components[{index}]"
        _object(component, {"order", "component", "control", "transforms", "provenance"}, path)
        order = component["order"]
        if isinstance(order, bool) or not isinstance(order, int) or order < 1:
            raise ValueError(f"{path}.order must be a positive integer")
        if order in orders:
            raise ValueError(f"duplicate path component order: {order}")
        orders.add(order)
        _string(component["component"], f"{path}.component")
        _enum(
            component["control"],
            CONTROL_CLASSIFICATIONS,
            f"{path}.control",
        )
        _string_list(component["transforms"], f"{path}.transforms", allow_empty=True)
        _validate_provenance(
            component["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )
    _string_list(filename["sanitization"], "producer_notes.filename_dataflow.sanitization")
    _string(filename["collision_behavior"], "producer_notes.filename_dataflow.collision_behavior")
    _string(filename["overwrite_behavior"], "producer_notes.filename_dataflow.overwrite_behavior")
    _validate_provenance(
        filename["provenance"],
        source_ids,
        "producer_notes.filename_dataflow.provenance",
        evidence_binding_ids,
    )

    html = _object(
        row["html_generation"],
        {"classification", "template_owner", "fields", "provenance"},
        "producer_notes.html_generation",
    )
    _enum(
        html["classification"],
        {"fixed_template_runtime_values", "partially_user_controlled", "arbitrary_content", "unknown"},
        "producer_notes.html_generation.classification",
    )
    _string(html["template_owner"], "producer_notes.html_generation.template_owner")
    html_fields = _list(html["fields"], "producer_notes.html_generation.fields")
    _unique_ids(html_fields, "html_generation.fields")
    field_names = {
        "id",
        "output_context",
        "value_source",
        "control",
        "encoding_or_escaping",
        "provenance",
    }
    for index, field in enumerate(html_fields):
        path = f"producer_notes.html_generation.fields[{index}]"
        _object(field, field_names, path)
        for key in ("id", "output_context", "value_source", "encoding_or_escaping"):
            _string(field[key], f"{path}.{key}")
        _enum(
            field["control"],
            CONTROL_CLASSIFICATIONS,
            f"{path}.control",
        )
        _validate_provenance(
            field["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )
    _validate_provenance(
        html["provenance"],
        source_ids,
        "producer_notes.html_generation.provenance",
        evidence_binding_ids,
    )

    signatures = _list(
        row["failure_signatures"], "producer_notes.failure_signatures", allow_empty=True
    )
    _unique_ids(signatures, "failure_signatures")
    signature_fields = {
        "id",
        "packaged_string",
        "resource_id",
        "caller",
        "trigger",
        "resulting_ui",
        "retry",
        "partial_file_state",
        "inferred_meaning",
        "provenance",
    }
    for index, signature in enumerate(signatures):
        path = f"producer_notes.failure_signatures[{index}]"
        _object(signature, signature_fields, path)
        for key in signature_fields - {"provenance"}:
            _string(signature[key], f"{path}.{key}")
        _validate_provenance(
            signature["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )

    _validate_unresolved_gates(
        row["unresolved_gates"],
        source_ids,
        evidence_binding_ids,
        "producer_notes.unresolved_gates",
    )
    return row


def _validate_status_provenance(
    value: Any,
    statuses: set[str],
    source_ids: set[str],
    evidence_binding_ids: set[str],
    path: str,
) -> None:
    row = _object(value, {"status", "provenance"}, path)
    status = _enum(row["status"], statuses, f"{path}.status")
    _validate_provenance(
        row["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
    )
    label = row["provenance"]["label"]
    if status == "proved" and label != "PROVED":
        raise ValueError(f"{path} status proved requires PROVED evidence")
    if status == "unknown" and label not in {"UNKNOWN", "TARGET OBSERVATION REQUIRED"}:
        raise ValueError(f"{path} status unknown requires unresolved evidence")


def validate_storage_notes(notes: Any) -> dict[str, Any]:
    fields = {
        "schema_version",
        "scope",
        "evidence_labels",
        "source_artifacts",
        "class_evidence_selections",
        "storage_destinations",
        "file_write_capability",
        "consumers",
        "handoffs",
        "unresolved_gates",
    }
    row, source_ids = _validate_common(notes, fields, "storage_notes")
    evidence_binding_ids = _validate_class_evidence_selections(
        row["class_evidence_selections"],
        source_ids,
        "storage_notes.class_evidence_selections",
    )

    destinations = _list(row["storage_destinations"], "storage_notes.storage_destinations")
    _unique_ids(destinations, "storage_destinations")
    destination_fields = {
        "id",
        "medium",
        "mount_or_service",
        "selection_logic",
        "write_scope",
        "provenance",
    }
    for index, destination in enumerate(destinations):
        path = f"storage_notes.storage_destinations[{index}]"
        _object(destination, destination_fields, path)
        for key in destination_fields - {"provenance"}:
            _string(destination[key], f"{path}.{key}")
        _validate_provenance(
            destination["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )

    capability = _object(
        row["file_write_capability"],
        {"level", "title", "justification", "limitations", "provenance"},
        "storage_notes.file_write_capability",
    )
    level = capability["level"]
    if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 5:
        raise ValueError("storage_notes.file_write_capability.level must be an integer from 0 to 5")
    _string(capability["title"], "storage_notes.file_write_capability.title")
    _string(capability["justification"], "storage_notes.file_write_capability.justification")
    _string_list(capability["limitations"], "storage_notes.file_write_capability.limitations")
    _validate_provenance(
        capability["provenance"],
        source_ids,
        "storage_notes.file_write_capability.provenance",
        evidence_binding_ids,
    )

    consumers = _list(row["consumers"], "storage_notes.consumers", allow_empty=True)
    _unique_ids(consumers, "consumers")
    consumer_fields = {
        "id",
        "application",
        "read_behavior",
        "filename_or_content_match",
        "static_reference",
        "runtime_reachability",
    }
    for index, consumer in enumerate(consumers):
        path = f"storage_notes.consumers[{index}]"
        _object(consumer, consumer_fields, path)
        for key in ("id", "application", "read_behavior", "filename_or_content_match"):
            _string(consumer[key], f"{path}.{key}")
        _validate_status_provenance(
            consumer["static_reference"],
            {"present", "absent", "unknown"},
            source_ids,
            evidence_binding_ids,
            f"{path}.static_reference",
        )
        _validate_status_provenance(
            consumer["runtime_reachability"],
            {"proved", "not_proved", "gated", "unknown"},
            source_ids,
            evidence_binding_ids,
            f"{path}.runtime_reachability",
        )

    handoffs = _list(row["handoffs"], "storage_notes.handoffs", allow_empty=True)
    _unique_ids(handoffs, "handoffs")
    handoff_fields = {
        "id",
        "producer",
        "storage",
        "consumer",
        "write_side",
        "read_side",
        "end_to_end_status",
        "constraints",
        "provenance",
    }
    handoff_statuses = {"proved", "not_proved", "gated", "unknown"}
    for index, handoff in enumerate(handoffs):
        path = f"storage_notes.handoffs[{index}]"
        _object(handoff, handoff_fields, path)
        for key in ("id", "producer", "storage", "consumer"):
            _string(handoff[key], f"{path}.{key}")
        _validate_status_provenance(
            handoff["write_side"],
            handoff_statuses,
            source_ids,
            evidence_binding_ids,
            f"{path}.write_side",
        )
        _validate_status_provenance(
            handoff["read_side"],
            handoff_statuses,
            source_ids,
            evidence_binding_ids,
            f"{path}.read_side",
        )
        end_status = _enum(
            handoff["end_to_end_status"], handoff_statuses, f"{path}.end_to_end_status"
        )
        _string_list(handoff["constraints"], f"{path}.constraints", allow_empty=True)
        _validate_provenance(
            handoff["provenance"], source_ids, f"{path}.provenance", evidence_binding_ids
        )
        if end_status == "proved":
            if handoff["write_side"]["status"] != "proved" or handoff["read_side"]["status"] != "proved":
                raise ValueError(f"{path} cannot prove an end-to-end handoff without both proved sides")
            if handoff["provenance"]["label"] != "PROVED":
                raise ValueError(f"{path} end-to-end status proved requires PROVED evidence")

    _validate_unresolved_gates(
        row["unresolved_gates"],
        source_ids,
        evidence_binding_ids,
        "storage_notes.unresolved_gates",
    )
    return row


def _load_notes(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"notes are not UTF-8: {path}") from exc
    value = strict_json_loads(text)
    if not isinstance(value, dict):
        raise ValueError(f"notes must contain one JSON object: {path}")
    return value, raw


def _collect_source_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        if set(value) == PROVENANCE_FIELDS:
            found.update(value["source_ids"])
        for child in value.values():
            found.update(_collect_source_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect_source_ids(child))
    return found


def _source_subset(value: Any, source_artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_ids = _collect_source_ids(value)
    return sorted(
        (source for source in source_artifacts if source["id"] in source_ids),
        key=lambda source: source["id"],
    )


def _sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: row["id"])


def _build_reports(
    producer: dict[str, Any],
    storage: dict[str, Any],
    producer_sha256: str,
    storage_sha256: str,
) -> dict[str, dict[str, Any]]:
    source_artifacts = sorted(
        [*producer["source_artifacts"], *storage["source_artifacts"]],
        key=lambda source: source["id"],
    )
    input_hashes = {
        "producer_notes": producer_sha256,
        "storage_consumer_notes": storage_sha256,
    }
    unresolved = _sorted_rows(
        [*producer["unresolved_gates"], *storage["unresolved_gates"]]
    )
    bindings = _sorted_rows(
        [
            *producer["class_evidence_selections"],
            *storage["class_evidence_selections"],
        ]
    )
    source_by_id = {source["id"]: source for source in source_artifacts}
    class_evidence = [
        {**binding, "source_sha256": source_by_id[binding["source_id"]]["sha256"]}
        for binding in bindings
    ]
    filename = producer["filename_dataflow"]
    html = producer["html_generation"]
    signatures = _sorted_rows(producer["failure_signatures"])

    summary = {
        "schema_version": 1,
        "scope": "Canonical static assessment of the stock Performance Pages removable-media export.",
        "evidence_labels": EVIDENCE_LABELS,
        "input_sha256": input_hashes,
        "source_artifacts": source_artifacts,
        "class_evidence_binding_ids": [binding["id"] for binding in bindings],
        "available_variants": _sorted_rows(producer["variants"]),
        "export_reachability": producer["export_reachability"],
        "storage_destinations": _sorted_rows(storage["storage_destinations"]),
        "filename_control_classification": filename["classification"],
        "content_control_classification": html["classification"],
        "file_write_capability": storage["file_write_capability"],
        "known_consumer_applications": _sorted_rows(storage["consumers"]),
        "potential_write_read_handoffs": _sorted_rows(storage["handoffs"]),
        "unresolved_gates": unresolved,
    }
    filename_report = {
        "schema_version": 1,
        "scope": "Performance Pages export filename and destination dataflow.",
        "evidence_labels": EVIDENCE_LABELS,
        "input_sha256": {"producer_notes": producer_sha256},
        "source_artifacts": _source_subset(filename, producer["source_artifacts"]),
        "classification": filename["classification"],
        "destination_source": filename["destination_source"],
        "path_components": sorted(filename["path_components"], key=lambda row: row["order"]),
        "sanitization": filename["sanitization"],
        "collision_behavior": filename["collision_behavior"],
        "overwrite_behavior": filename["overwrite_behavior"],
        "provenance": filename["provenance"],
    }
    html_report = {
        "schema_version": 1,
        "scope": "Performance Pages fixed template and runtime HTML field dataflow.",
        "evidence_labels": EVIDENCE_LABELS,
        "input_sha256": {"producer_notes": producer_sha256},
        "source_artifacts": _source_subset(html, producer["source_artifacts"]),
        "classification": html["classification"],
        "template_owner": html["template_owner"],
        "fields": _sorted_rows(html["fields"]),
        "provenance": html["provenance"],
    }
    failure_report = {
        "schema_version": 1,
        "scope": "Packaged Performance Pages export failure signatures and static lifecycle evidence.",
        "evidence_labels": EVIDENCE_LABELS,
        "input_sha256": {"producer_notes": producer_sha256},
        "source_artifacts": _source_subset(signatures, producer["source_artifacts"]),
        "signatures": signatures,
    }
    bound_source_ids = {binding["source_id"] for binding in bindings}
    class_report = {
        "schema_version": 1,
        "scope": (
            "Selected JVM method and instruction evidence parsed read-only from hash-bound "
            "stock JAR classfiles when --corpus is supplied."
        ),
        "evidence_labels": EVIDENCE_LABELS,
        "input_sha256": input_hashes,
        "source_artifacts": [
            source for source in source_artifacts if source["id"] in bound_source_ids
        ],
        "bindings": class_evidence,
    }
    return {
        "performance_pages_export_summary.json": summary,
        "performance_pages_export_class_evidence.json": class_report,
        "performance_pages_filename_dataflow.json": filename_report,
        "performance_pages_html_fields.json": html_report,
        "performance_pages_export_failure_signatures.json": failure_report,
    }


def prepare_reports(producer_path: Path, storage_path: Path) -> dict[str, dict[str, Any]]:
    producer, producer_raw = _load_notes(Path(producer_path))
    storage, storage_raw = _load_notes(Path(storage_path))
    validate_producer_notes(producer)
    validate_storage_notes(storage)

    producer_source_ids = {source["id"] for source in producer["source_artifacts"]}
    storage_source_ids = {source["id"] for source in storage["source_artifacts"]}
    duplicate_sources = sorted(producer_source_ids & storage_source_ids)
    if duplicate_sources:
        raise ValueError(f"duplicate source id across evidence inputs: {duplicate_sources[0]}")
    producer_binding_ids = {
        binding["id"] for binding in producer["class_evidence_selections"]
    }
    storage_binding_ids = {
        binding["id"] for binding in storage["class_evidence_selections"]
    }
    duplicate_bindings = sorted(producer_binding_ids & storage_binding_ids)
    if duplicate_bindings:
        raise ValueError(
            f"duplicate class evidence binding id across inputs: {duplicate_bindings[0]}"
        )
    producer_gate_ids = {gate["id"] for gate in producer["unresolved_gates"]}
    storage_gate_ids = {gate["id"] for gate in storage["unresolved_gates"]}
    duplicate_gates = sorted(producer_gate_ids & storage_gate_ids)
    if duplicate_gates:
        raise ValueError(f"duplicate unresolved gate id across evidence inputs: {duplicate_gates[0]}")

    return _build_reports(
        producer,
        storage,
        hashlib.sha256(producer_raw).hexdigest(),
        hashlib.sha256(storage_raw).hexdigest(),
    )


def verify_corpus_sources(
    corpus: Path,
    producer: dict[str, Any],
    storage: dict[str, Any],
) -> None:
    validate_producer_notes(producer)
    validate_storage_notes(storage)
    root = Path(corpus).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"corpus is not a directory: {root}")
    resolved_sources: dict[str, tuple[Path, bytes]] = {}
    for source in sorted(
        [*producer["source_artifacts"], *storage["source_artifacts"]],
        key=lambda row: row["id"],
    ):
        relative = PurePosixPath(source["corpus_relative_path"])
        candidate = root.joinpath(*relative.parts).resolve(strict=True)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                f"source resolves outside corpus for {source['id']}: {candidate}"
            ) from exc
        if not candidate.is_file():
            raise ValueError(f"source is not a file for {source['id']}: {candidate}")
        source_bytes = candidate.read_bytes()
        actual = hashlib.sha256(source_bytes).hexdigest()
        if actual != source["sha256"]:
            raise ValueError(
                f"source hash mismatch for {source['id']}: expected {source['sha256']}, got {actual}"
            )
        resolved_sources[source["id"]] = (candidate, source_bytes)

    bindings = sorted(
        [
            *producer["class_evidence_selections"],
            *storage["class_evidence_selections"],
        ],
        key=lambda row: row["id"],
    )
    for binding in bindings:
        jar_path, jar_bytes = resolved_sources[binding["source_id"]]
        try:
            with zipfile.ZipFile(io.BytesIO(jar_bytes)) as archive:
                member_name = f"{binding['class_name']}.class"
                matching = [info for info in archive.infolist() if info.filename == member_name]
                if len(matching) != 1:
                    raise ValueError(
                        f"class evidence binding {binding['id']} expected one {member_name}, "
                        f"found {len(matching)}"
                    )
                class_bytes = archive.read(matching[0])
        except zipfile.BadZipFile as exc:
            raise ValueError(
                f"class evidence source is not a valid JAR for {binding['id']}: {jar_path}"
            ) from exc
        actual_class_sha256 = hashlib.sha256(class_bytes).hexdigest()
        if actual_class_sha256 != binding["class_sha256"]:
            raise ValueError(
                f"class hash mismatch for {binding['id']}: expected "
                f"{binding['class_sha256']}, got {actual_class_sha256}"
            )
        model = parse_class(class_bytes)
        if model.name != binding["class_name"]:
            raise ValueError(
                f"class identity mismatch for {binding['id']}: {model.name}"
            )
        method = model.method(binding["method_name"], binding["descriptor"])
        if len(method.instructions) != binding["instruction_count"]:
            raise ValueError(
                f"instruction count mismatch for {binding['id']}: expected "
                f"{binding['instruction_count']}, got {len(method.instructions)}"
            )
        members = {
            (
                edge.offset,
                edge.opcode,
                edge.owner,
                edge.name,
                edge.descriptor,
            )
            for edge in method.member_edges
        }
        strings = {
            (edge.offset, edge.opcode, edge.value)
            for edge in method.literal_edges
            if isinstance(edge.value, str)
        }
        for selection in binding["selected_instructions"]:
            if selection["kind"] == "member":
                expected = (
                    selection["bci"],
                    selection["opcode"],
                    selection["owner"],
                    selection["name"],
                    selection["descriptor"],
                )
                matched = expected in members
            else:
                expected = (
                    selection["bci"],
                    selection["opcode"],
                    selection["value"],
                )
                matched = expected in strings
            if not matched:
                raise ValueError(
                    f"selected instruction mismatch for {binding['id']}: {selection}"
                )


def generate_reports(
    producer_path: Path,
    storage_path: Path,
    report_dir: Path,
    *,
    check: bool = False,
    corpus: Path | None = None,
) -> int:
    producer_path = Path(producer_path)
    storage_path = Path(storage_path)
    report_dir = Path(report_dir)
    if corpus is not None:
        corpus_root = Path(corpus).resolve(strict=True)
        prospective_report_dir = report_dir.resolve(strict=False)
        try:
            prospective_report_dir.relative_to(corpus_root)
        except ValueError:
            pass
        else:
            raise ValueError(
                f"report directory must be outside corpus: {prospective_report_dir}"
            )
    reports = prepare_reports(producer_path, storage_path)
    if corpus is not None:
        producer, _ = _load_notes(producer_path)
        storage, _ = _load_notes(storage_path)
        verify_corpus_sources(Path(corpus), producer, storage)

    expected = {name: canonical_bytes(reports[name]) for name in REPORT_FILENAMES}
    if check:
        return 0 if all(
            (report_dir / name).is_file() and (report_dir / name).read_bytes() == payload
            for name, payload in expected.items()
        ) else 1

    report_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in expected.items():
        destination = report_dir / name
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_bytes(payload)
        temporary.replace(destination)
    return 0
