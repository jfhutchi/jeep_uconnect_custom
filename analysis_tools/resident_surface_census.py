"""Read-only resident Java archive and extension-surface census.

Recovered artifacts are opened in place and never extracted or executed.  The
output contains hashes, relative paths, names, and parsed structural edges; it
does not contain class/resource payload bytes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable, Mapping
import warnings
import xml.etree.ElementTree as ET
import zipfile

from analysis_tools.activation_graph import (
    ActivationGraph, CallEdge, MethodNode,
)
from analysis_tools.evidence_model import ACTIVATION_STATES, write_json
from analysis_tools.java_classfile import ClassModel, parse_class


TOOL_VERSION = "1.0"

OUTPUT_FILENAMES = (
    "activation_call_paths.json",
    "java_extension_surfaces.json",
    "network_ipc_endpoints.json",
    "user_controlled_input_surfaces.json",
)


@dataclass(frozen=True)
class ScanLimits:
    max_archives: int = 2_000
    max_classes: int = 200_000
    max_member_bytes: int = 8 * 1024 * 1024
    max_archive_bytes: int = 512 * 1024 * 1024
    max_total_bytes: int = 4 * 1024 * 1024 * 1024
    max_resource_bytes: int = 512 * 1024

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")


def _lower_pair(owner: str, name: str, class_name: str) -> str:
    return f"{owner} {name} {class_name}".lower()


def classify_reference(
    owner: str, name: str, descriptor: str, class_name: str,
) -> tuple[str, ...]:
    """Classify one parsed member reference without claiming runtime use."""
    del descriptor
    text = _lower_pair(owner, name, class_name)
    categories = set()
    if (
        owner in ("java/lang/ClassLoader", "java/net/URLClassLoader")
        or (owner == "java/lang/Class" and name in ("forName", "newInstance"))
        or name in ("loadClass", "defineClass", "findClass")
    ):
        categories.add("dynamic_loading")
    if "java/lang/reflect/" in owner or (
        owner == "java/lang/Class"
        and name.startswith(("getMethod", "getDeclared", "getField", "getConstructor"))
    ):
        categories.add("reflection")
    if "factory" in text or "provider" in text and name.lower().startswith(
        ("create", "get", "new", "register", "set")
    ):
        categories.add("factory_provider")
    if (
        owner.startswith(("java/util/jar/", "java/util/zip/"))
        or name in ("getResource", "getResourceAsStream", "getPackage")
    ):
        categories.add("resource_package_loading")
    if any(marker in text for marker in (
        "javascript", "mozilla", "rhino", "lua", "scriptengine", "interpreter",
    )) or name in ("eval", "evaluate", "evaluateString"):
        categories.add("scripting_interpreter")
    if owner.startswith(("java/net/URL", "java/net/URI")) or any(
        marker in owner for marker in ("URLStreamHandler", "URLConnection")
    ):
        categories.add("url_protocol")
    if "webkit" in text or "browser" in text or "webview" in text:
        categories.add("browser_webkit")
    if owner.startswith((
        "javax/xml/", "org/xml/", "org/json/", "com/google/gson/",
    )) or owner in ("java/util/Properties",):
        categories.add("structured_data")
    if owner.startswith("java/net/") and any(marker in owner for marker in (
        "Socket", "ServerSocket", "Datagram", "InetAddress",
    )):
        categories.add("network_service")
    if any(marker in text for marker in (
        "svcipc", "/ipc", "messagechannel", "serviceproxy", "serviceregistry",
    )):
        categories.add("ipc_service")
    if any(marker in text for marker in (
        "/media/", "mediaimport", "importer", "playlist", "metadata",
    )) and any(marker in name.lower() for marker in (
        "import", "load", "parse", "scan", "read", "play", "metadata",
    )):
        categories.add("media_import")
    if owner.startswith("java/io/") and any(marker in owner for marker in (
        "File", "InputStream", "Reader",
    )):
        categories.add("user_file_resource")
    if "plugin" in text or "registry" in text and any(
        marker in name.lower() for marker in ("register", "provider", "plugin")
    ):
        categories.add("plugin_registration")
    return tuple(sorted(categories))


def _unescape_property(value: str) -> str:
    result = []
    index = 0
    escapes = {"t": "\t", "n": "\n", "r": "\r", "f": "\f"}
    while index < len(value):
        if value[index] != "\\":
            result.append(value[index])
            index += 1
            continue
        index += 1
        if index >= len(value):
            result.append("\\")
            break
        marker = value[index]
        index += 1
        if marker == "u":
            if index + 4 > len(value):
                raise ValueError("truncated Java properties Unicode escape")
            digits = value[index:index + 4]
            if not re.fullmatch(r"[0-9A-Fa-f]{4}", digits):
                raise ValueError("invalid Java properties Unicode escape")
            result.append(chr(int(digits, 16)))
            index += 4
        else:
            result.append(escapes.get(marker, marker))
    return "".join(result)


def _logical_property_lines(text: str) -> list[str]:
    lines = text.splitlines()
    result = []
    current = ""
    for physical in lines:
        current += physical.lstrip() if current else physical
        backslashes = len(current) - len(current.rstrip("\\"))
        if backslashes % 2:
            current = current[:-1]
            continue
        result.append(current)
        current = ""
    if current:
        result.append(current)
    return result


def parse_properties(data: bytes) -> dict[str, Any]:
    """Parse Java properties with last-value semantics and duplicate evidence."""
    text = data.decode("iso-8859-1")
    entries: list[list[str]] = []
    values: dict[str, str] = {}
    duplicates: list[str] = []
    for raw_line in _logical_property_lines(text):
        stripped = raw_line.lstrip()
        if not stripped or stripped.startswith(("#", "!")):
            continue
        separator = None
        escaped = False
        for index, character in enumerate(stripped):
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character in "=:" or character.isspace():
                separator = index
                break
        if separator is None:
            raw_key, raw_value = stripped, ""
        else:
            raw_key = stripped[:separator]
            cursor = separator
            while cursor < len(stripped) and stripped[cursor].isspace():
                cursor += 1
            if cursor < len(stripped) and stripped[cursor] in "=:":
                cursor += 1
            while cursor < len(stripped) and stripped[cursor].isspace():
                cursor += 1
            raw_value = stripped[cursor:]
        key = _unescape_property(raw_key)
        value = _unescape_property(raw_value)
        if key in values and key not in duplicates:
            duplicates.append(key)
        entries.append([key, value])
        values[key] = value
    return {"entries": entries, "values": values, "duplicates": duplicates}


def _hash_path(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _artifact_name(label: str, relative: str) -> str:
    return f"{label}/{relative.replace(os.sep, '/')}"


def _walk_inputs(label: str, root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    if not root.is_dir():
        raise ValueError(f"input root is not a directory: {label}")
    paths = []
    errors = []
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_directories = []
        for directory in sorted(directories, key=str.lower):
            candidate = current_path / directory
            if candidate.is_symlink():
                errors.append({
                    "artifact": _artifact_name(label, candidate.relative_to(root).as_posix()),
                    "message": "symlink directory skipped",
                })
            else:
                kept_directories.append(directory)
        directories[:] = kept_directories
        for filename in sorted(files, key=str.lower):
            candidate = current_path / filename
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_symlink():
                errors.append({
                    "artifact": _artifact_name(label, relative),
                    "message": "symlink file skipped",
                })
            elif candidate.suffix.lower() in (".jar", ".zip", ".class"):
                paths.append(candidate)
    paths.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    return paths, errors


def _safe_member(name: str) -> bool:
    pure = PurePosixPath(name.replace("\\", "/"))
    return not pure.is_absolute() and ".." not in pure.parts and not re.match(
        r"^[A-Za-z]:", name
    )


_CLASS_NAME = re.compile(
    r"(?<![A-Za-z0-9_$])(?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}"
    r"[A-Za-z_$][A-Za-z0-9_$]*(?![A-Za-z0-9_$])"
)


def _configured_names(value: Any) -> list[str]:
    names = set()
    if isinstance(value, str):
        names.update(_CLASS_NAME.findall(value))
    elif isinstance(value, Mapping):
        for item in value.values():
            names.update(_configured_names(item))
    elif isinstance(value, list):
        for item in value:
            names.update(_configured_names(item))
    return sorted(names)


def _resource_metadata(name: str, data: bytes) -> dict[str, Any] | None:
    suffix = PurePosixPath(name).suffix.lower()
    if suffix in (".properties", ".mf") or name.upper().endswith("MANIFEST.MF"):
        parsed = parse_properties(data)
        return {
            "kind": "properties", "member": name,
            "keys": sorted(parsed["values"]),
            "duplicates": parsed["duplicates"],
            "configured_classes": _configured_names(parsed["values"]),
        }
    if suffix == ".json":
        parsed = json.loads(data.decode("utf-8-sig"))
        return {
            "kind": "json", "member": name,
            "configured_classes": _configured_names(parsed),
        }
    if suffix == ".xml":
        text = data.decode("utf-8-sig")
        if re.search(r"<!\s*(DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
            raise ValueError("XML external declaration rejected")
        root = ET.fromstring(text)
        values = []
        for element in root.iter():
            values.extend(element.attrib.values())
            if element.text:
                values.append(element.text)
        return {
            "kind": "xml", "member": name,
            "root_tag": root.tag,
            "configured_classes": _configured_names(values),
        }
    return None


def _source(artifact: str, member: str, offset: int, kind: str = "bytecode_edge") -> dict[str, Any]:
    return {
        "kind": kind,
        "artifact": artifact,
        "member": member,
        "offset": offset,
    }


def _method_id(owner: str, name: str, descriptor: str) -> str:
    return f"{owner}#{name}{descriptor}"


def _root_categories(model: ClassModel, method_name: str) -> tuple[str, ...]:
    categories = set()
    if method_name in ("initXlet", "startXlet", "pauseXlet", "destroyXlet"):
        categories.add("xlet_lifecycle")
    if method_name in (
        "actionPerformed", "keyPressed", "keyReleased", "pointerPressed",
        "pointerReleased", "onItem", "onClick",
    ):
        categories.add("ui_callback")
    if method_name.startswith(("onMessage", "onEvent", "serviceChanged", "callback")):
        categories.add("service_callback")
    if method_name == "run" and "java/lang/Runnable" in model.interfaces:
        categories.add("thread_runnable")
    simple = model.name.rsplit("/", 1)[-1]
    if simple.endswith(("Test", "Tests", "TestCase")) or method_name.startswith("test"):
        categories.add("test_framework")
    if "Factory" in simple and method_name.startswith(("create", "get", "new")):
        categories.add("factory_provider")
    if method_name.lower().startswith("register"):
        categories.add("registration")
    if method_name == "main":
        categories.add("unknown_external_entry")
    return tuple(category for category in (
        "xlet_lifecycle", "ui_callback", "service_callback", "configuration",
        "registration", "factory_provider", "feature_flag", "thread_runnable",
        "test_framework", "unknown_external_entry",
    ) if category in categories)


def resolve_focus_dispatch_candidates(
    models_by_name: Mapping[str, ClassModel], focus_class: str,
) -> list[tuple[str, str, str, int, str, str, str, str]]:
    """Resolve virtual calls to focus overrides without claiming runtime dispatch.

    The result is deliberately labelled as a candidate.  It establishes the
    structural consumer path which a direct constant-pool owner would otherwise
    hide, but it does not prove the receiver's runtime type.
    """
    focus = models_by_name.get(focus_class)
    if focus is None:
        return []
    ancestors: set[str] = set()
    pending = [focus.super_name, *focus.interfaces]
    while pending:
        owner = pending.pop()
        if owner is None or owner in ancestors:
            continue
        ancestors.add(owner)
        model = models_by_name.get(owner)
        if model is not None:
            pending.extend((model.super_name, *model.interfaces))
    overrides = {
        (method.name, method.descriptor)
        for method in focus.methods
        if method.name not in ("<init>", "<clinit>")
    }
    candidates = []
    for caller_name, caller in sorted(models_by_name.items()):
        for method in caller.methods:
            for edge in method.member_edges:
                if (
                    edge.kind in ("invoke_virtual", "invoke_interface")
                    and edge.owner in ancestors
                    and (edge.name, edge.descriptor) in overrides
                ):
                    relation = (
                        "superclass_virtual_override_candidate"
                        if edge.kind == "invoke_virtual"
                        else "interface_override_candidate"
                    )
                    candidates.append((
                        caller_name, method.name, method.descriptor, edge.offset,
                        focus_class, edge.name, edge.descriptor, relation,
                    ))
    return sorted(candidates)


def _method_details(method: Any) -> dict[str, Any]:
    return {
        "name": method.name,
        "descriptor": method.descriptor,
        "access_flags": method.access_flags,
        "native": method.is_native,
        "abstract": method.is_abstract,
        "instructions": [
            {
                "offset": instruction.offset,
                "mnemonic": instruction.mnemonic,
                "operands": list(instruction.operands),
                "targets": list(instruction.target_offsets),
            }
            for instruction in method.instructions
        ],
        "member_edges": [asdict(edge) for edge in method.member_edges],
        "type_edges": [asdict(edge) for edge in method.type_edges],
        "literal_edges": [asdict(edge) for edge in method.literal_edges],
        "exception_handlers": [asdict(handler) for handler in method.exception_handlers],
    }


def _focus_model(model: ClassModel) -> dict[str, Any]:
    return {
        "name": model.name,
        "super_name": model.super_name,
        "interfaces": list(model.interfaces),
        "major_version": model.major_version,
        "access_flags": model.access_flags,
        "fields": [
            {
                "name": field.name,
                "descriptor": field.descriptor,
                "access_flags": field.access_flags,
                "constant_value": field.constant_value,
            }
            for field in model.fields
        ],
        "methods": [_method_details(method) for method in model.methods],
        "class_references": list(model.class_references),
        "string_constants": list(model.string_constants),
    }


def _capability_for(category: str) -> str:
    return {
        "dynamic_loading": "load a class selected by resident code or configuration",
        "reflection": "inspect or invoke a resident member selected at runtime",
        "factory_provider": "select or construct a resident implementation",
        "resource_package_loading": "read an archive or packaged resource",
        "scripting_interpreter": "evaluate input through a resident interpreter API",
        "url_protocol": "resolve or open a URL/URI protocol resource",
        "browser_webkit": "navigate or exchange data with a browser surface",
        "structured_data": "parse structured properties, XML, or JSON data",
        "network_service": "create or use a Java network endpoint",
        "ipc_service": "exchange a request or event through a resident service API",
        "media_import": "scan, import, parse, or play media data",
        "user_file_resource": "read a file or stream visible to the resident app",
        "plugin_registration": "register or select a provider-like component",
        "configured_class": "select a resident class by configured name",
    }.get(category, "use the referenced resident API")


def _surface(
    *, category: str, class_name: str, method_id: str, artifact: str,
    member: str, offset: int, reference: str,
) -> dict[str, Any]:
    identifier = hashlib.sha256(
        f"{category}\0{class_name}\0{method_id}\0{reference}".encode("utf-8")
    ).hexdigest()[:20]
    return {
        "id": identifier,
        "category": category,
        "classification": "PROVED",
        "claim": "parsed static presence in recovered resident bytecode or configuration",
        "component": class_name,
        "method": method_id,
        "reference": reference,
        "origin": {
            "classification": "UNKNOWN",
            "description": "external or user-controlled origin not established by this edge",
        },
        "signed_component": {
            "classification": "UNKNOWN",
            "description": "installed executable presence is parsed; signer association is not evaluated here",
        },
        "parser": {
            "classification": "PROVED" if category == "structured_data" else "UNKNOWN",
            "description": reference if category == "structured_data" else "parser not established",
        },
        "dispatcher": {"classification": "UNKNOWN", "description": "not established"},
        "capability": {
            "classification": "STRONGLY INFERRED",
            "description": _capability_for(category),
        },
        "missing_links": [
            "external_origin", "signed_runtime_activation", "dispatcher",
            "resulting_runtime_capability",
        ],
        "sources": [_source(artifact, member, offset)],
    }


def census_roots(
    roots: Mapping[str, Path], *, focus_class: str | None,
    broad: bool, limits: ScanLimits | None = None,
) -> dict[str, Any]:
    """Census labeled roots and return a normalized in-memory result."""
    if not roots:
        raise ValueError("at least one labeled input root is required")
    limits = limits or ScanLimits()
    limits.validate()
    normalized_roots = {label: Path(path) for label, path in roots.items()}
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", label) for label in normalized_roots):
        raise ValueError("input labels may contain only letters, digits, dot, dash, underscore")

    inputs: list[tuple[str, Path, Path]] = []
    errors: list[dict[str, Any]] = []
    for label in sorted(normalized_roots):
        discovered, root_errors = _walk_inputs(label, normalized_roots[label])
        errors.extend(root_errors)
        inputs.extend((label, normalized_roots[label], path) for path in discovered)
    archive_count = sum(path.suffix.lower() in (".jar", ".zip") for _, _, path in inputs)
    if archive_count > limits.max_archives:
        raise ValueError(f"archive limit exceeded: {archive_count} > {limits.max_archives}")

    manifest = []
    occurrences: list[dict[str, Any]] = []
    resource_records: list[dict[str, Any]] = []
    models_by_hash: dict[str, ClassModel] = {}
    first_source_by_hash: dict[str, tuple[str, str]] = {}
    class_occurrences = 0
    total_bytes = 0

    def consume_class(data: bytes, artifact: str, member: str) -> None:
        nonlocal class_occurrences, total_bytes
        class_occurrences += 1
        total_bytes += len(data)
        if class_occurrences > limits.max_classes:
            raise ValueError(f"class limit exceeded: {class_occurrences} > {limits.max_classes}")
        if total_bytes > limits.max_total_bytes:
            raise ValueError("total uncompressed byte limit exceeded")
        if len(data) > limits.max_member_bytes:
            errors.append({"artifact": artifact, "member": member, "message": "class member size limit exceeded"})
            return
        digest = hashlib.sha256(data).hexdigest()
        occurrence = {"artifact": artifact, "member": member, "sha256": digest, "bytes": len(data)}
        occurrences.append(occurrence)
        if digest in models_by_hash:
            return
        try:
            model = parse_class(data, max_class_bytes=limits.max_member_bytes)
        except ValueError as error:
            errors.append({"artifact": artifact, "member": member, "message": str(error)})
            return
        models_by_hash[digest] = model
        first_source_by_hash[digest] = (artifact, member)

    for label, root, path in inputs:
        relative = path.relative_to(root).as_posix()
        artifact = _artifact_name(label, relative)
        digest = _hash_path(path)
        manifest.append({"artifact": artifact, "sha256": digest, "bytes": path.stat().st_size})
        if path.suffix.lower() == ".class":
            consume_class(path.read_bytes(), artifact, relative)
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive = zipfile.ZipFile(path)
            with archive:
                infos = archive.infolist()
                archive_total = sum(info.file_size for info in infos if not info.is_dir())
                if archive_total > limits.max_archive_bytes:
                    errors.append({"artifact": artifact, "message": "archive uncompressed size limit exceeded"})
                    continue
                seen = set()
                for info in infos:
                    name = info.filename
                    if info.is_dir():
                        continue
                    if not _safe_member(name):
                        errors.append({"artifact": artifact, "member": name, "message": "unsafe archive member path"})
                        continue
                    if name in seen:
                        errors.append({"artifact": artifact, "member": name, "message": "duplicate archive member"})
                        continue
                    seen.add(name)
                    if info.file_size > limits.max_member_bytes:
                        if name.endswith(".class"):
                            errors.append({"artifact": artifact, "member": name, "message": "class member size limit exceeded"})
                        continue
                    if name.endswith(".class"):
                        with archive.open(info) as stream:
                            data = stream.read(limits.max_member_bytes + 1)
                        if len(data) != info.file_size:
                            errors.append({"artifact": artifact, "member": name, "message": "class member size mismatch"})
                            continue
                        consume_class(data, artifact, name)
                    elif info.file_size <= limits.max_resource_bytes:
                        suffix = PurePosixPath(name).suffix.lower()
                        if suffix not in (".properties", ".mf", ".xml", ".json") and not name.upper().endswith("MANIFEST.MF"):
                            continue
                        with archive.open(info) as stream:
                            data = stream.read(limits.max_resource_bytes + 1)
                        try:
                            metadata = _resource_metadata(name, data)
                        except (UnicodeError, ValueError, ET.ParseError, json.JSONDecodeError) as error:
                            errors.append({"artifact": artifact, "member": name, "message": f"resource parse error: {error}"})
                            continue
                        if metadata is not None:
                            resource_records.append({"artifact": artifact, **metadata})
        except (OSError, zipfile.BadZipFile, RuntimeError) as error:
            errors.append({"artifact": artifact, "message": f"archive error: {error}"})

    for occurrence in occurrences:
        model = models_by_hash.get(occurrence["sha256"])
        if model is not None:
            occurrence["class"] = model.name
    occurrences.sort(key=lambda row: (row["artifact"], row["member"], row["sha256"]))
    focus_occurrences = []
    focus_hashes = []
    for occurrence in occurrences:
        model = models_by_hash.get(occurrence["sha256"])
        if model is not None and model.name == focus_class:
            focus_occurrences.append(occurrence)
            focus_hashes.append(occurrence["sha256"])
    if focus_class and not focus_occurrences:
        parse_failures = [
            error for error in errors
            if error.get("member", "").endswith(focus_class + ".class")
        ]
        if parse_failures:
            raise ValueError(f"focus class failed to parse: {focus_class}")

    surfaces = []
    for digest, model in sorted(models_by_hash.items(), key=lambda item: (item[1].name, item[0])):
        artifact, member = first_source_by_hash[digest]
        for method in model.methods:
            identifier = _method_id(model.name, method.name, method.descriptor)
            for edge in method.member_edges:
                categories = classify_reference(
                    edge.owner, edge.name, edge.descriptor, model.name
                )
                for category in categories:
                    surfaces.append(_surface(
                        category=category, class_name=model.name,
                        method_id=identifier, artifact=artifact, member=member,
                        offset=edge.offset,
                        reference=f"{edge.owner}#{edge.name}{edge.descriptor}",
                    ))

    for resource in resource_records:
        for configured_class in resource.get("configured_classes", []):
            surfaces.append(_surface(
                category="configured_class", class_name=configured_class,
                method_id="<configuration>", artifact=resource["artifact"],
                member=resource["member"], offset=0,
                reference=configured_class.replace(".", "/"),
            ))

    occurrences_by_artifact: dict[str, list[dict[str, Any]]] = {}
    for occurrence in occurrences:
        if "class" in occurrence:
            occurrences_by_artifact.setdefault(occurrence["artifact"], []).append(occurrence)

    focus_references = []
    if focus_class:
        for occurrence in occurrences:
            model = models_by_hash.get(occurrence["sha256"])
            if model is None or model.name == focus_class:
                continue
            reference_kinds = []
            if focus_class in model.class_references:
                reference_kinds.append("constant_pool_class")
            if focus_class.replace("/", ".") in model.string_constants:
                reference_kinds.append("constant_string")
            for method in model.methods:
                if any(edge.owner == focus_class for edge in method.member_edges):
                    reference_kinds.append("bytecode_member")
                if any(edge.owner == focus_class for edge in method.type_edges):
                    reference_kinds.append("bytecode_type")
                if any(
                    edge.kind == "string_literal"
                    and edge.value in (focus_class, focus_class.replace("/", "."))
                    for edge in method.literal_edges
                ):
                    reference_kinds.append("loaded_class_name_string")
            if reference_kinds:
                focus_references.append({
                    "class": model.name,
                    "class_sha256": occurrence["sha256"],
                    "artifact": occurrence["artifact"],
                    "member": occurrence["member"],
                    "reference_kinds": sorted(set(reference_kinds)),
                })

    focus_artifacts = sorted({row["artifact"] for row in focus_occurrences})
    focus_nodes: dict[str, MethodNode] = {}
    focus_edges: list[CallEdge] = []
    focus_edge_rows = []
    focus_dispatch_candidates = []
    focus_context: dict[str, tuple[str, ClassModel, Any, dict[str, Any]]] = {}
    for artifact in focus_artifacts:
        class_rows: dict[str, dict[str, Any]] = {}
        for occurrence in occurrences_by_artifact.get(artifact, []):
            class_name = occurrence["class"]
            if class_name in class_rows:
                errors.append({
                    "artifact": artifact,
                    "member": occurrence["member"],
                    "message": f"duplicate class definition in archive: {class_name}",
                })
                continue
            class_rows[class_name] = occurrence
        for class_name, occurrence in sorted(class_rows.items()):
            model = models_by_hash[occurrence["sha256"]]
            for method in model.methods:
                symbolic = _method_id(class_name, method.name, method.descriptor)
                identifier = f"{artifact}!{symbolic}"
                focus_nodes[identifier] = MethodNode(
                    identifier, class_name, method.name, method.descriptor,
                    _root_categories(model, method.name),
                    (_source(artifact, occurrence["member"], 0, "parsed_structure"),),
                )
                focus_context[identifier] = (
                    occurrence["sha256"], model, method, occurrence,
                )
        for class_name, occurrence in sorted(class_rows.items()):
            model = models_by_hash[occurrence["sha256"]]
            for method in model.methods:
                caller_symbolic = _method_id(class_name, method.name, method.descriptor)
                caller = f"{artifact}!{caller_symbolic}"
                for edge in method.member_edges:
                    if not edge.kind.startswith("invoke"):
                        continue
                    callee_symbolic = _method_id(edge.owner, edge.name, edge.descriptor)
                    callee = f"{artifact}!{callee_symbolic}"
                    resolved = callee in focus_nodes
                    call = CallEdge(
                        caller, callee, edge.kind, resolved,
                        _source(artifact, occurrence["member"], edge.offset),
                    )
                    focus_edges.append(call)
                    focus_edge_rows.append({
                        "caller": caller,
                        "callee": callee,
                        "kind": edge.kind,
                        "resolved": resolved,
                        "dispatch": (
                            "symbolic_candidate"
                            if edge.kind in ("invoke_virtual", "invoke_interface")
                            else "direct"
                        ),
                        "source": dict(call.source or {}),
                    })
        models_by_name = {
            class_name: models_by_hash[occurrence["sha256"]]
            for class_name, occurrence in class_rows.items()
        }
        for (
            caller_class, caller_name, caller_descriptor, offset,
            callee_class, callee_name, callee_descriptor, relation,
        ) in resolve_focus_dispatch_candidates(models_by_name, focus_class or ""):
            caller = f"{artifact}!{_method_id(caller_class, caller_name, caller_descriptor)}"
            callee = f"{artifact}!{_method_id(callee_class, callee_name, callee_descriptor)}"
            occurrence = class_rows[caller_class]
            resolved = caller in focus_nodes and callee in focus_nodes
            source = _source(artifact, occurrence["member"], offset)
            call = CallEdge(caller, callee, relation, resolved, source)
            focus_edges.append(call)
            row = {
                "caller": caller,
                "callee": callee,
                "kind": relation,
                "resolved": resolved,
                "dispatch": "structural_candidate_not_runtime_proof",
                "source": dict(source),
            }
            focus_edge_rows.append(row)
            focus_dispatch_candidates.append(row)

    relevant: set[str] = set()
    reverse_paths = []
    ladder = {
        state: {"classification": "UNKNOWN", "evidence": []}
        for state in ACTIVATION_STATES
    }
    strong_components: list[list[str]] = []
    if focus_nodes:
        graph = ActivationGraph.from_iterables(focus_nodes.values(), focus_edges)
        relevant.update(
            identifier for identifier, node in focus_nodes.items()
            if node.class_name == focus_class
        )
        changed = True
        while changed:
            changed = False
            for edge in focus_edges:
                if edge.resolved and edge.callee in relevant and edge.caller not in relevant:
                    relevant.add(edge.caller)
                    changed = True
        for identifier in sorted(
            value for value in relevant
            if focus_nodes[value].class_name == focus_class
        ):
            for path in graph.reverse_paths(identifier):
                reverse_paths.append({
                    "target": identifier,
                    "nodes": list(path.nodes),
                    "edge_kinds": list(path.edge_kinds),
                    "root_categories": list(path.root_categories),
                })
        ladder = graph.activation_ladder(focus_class)
        strong_components = [
            list(component) for component in graph.strong_components()
            if any(identifier in relevant for identifier in component)
        ]

    relevant_symbolic = {
        _method_id(
            focus_nodes[identifier].class_name,
            focus_nodes[identifier].method_name,
            focus_nodes[identifier].descriptor,
        )
        for identifier in relevant
    }
    context_methods = []
    for identifier in sorted(relevant):
        digest, model, method, occurrence = focus_context[identifier]
        context_methods.append({
            "id": identifier,
            "artifact": occurrence["artifact"],
            "member": occurrence["member"],
            "class_sha256": digest,
            "class": model.name,
            "super_name": model.super_name,
            "interfaces": list(model.interfaces),
            **_method_details(method),
        })

    if not broad:
        surfaces = [
            surface for surface in surfaces
            if surface["method"] in relevant_symbolic
            or surface["component"] == focus_class
            or surface["reference"] == (focus_class or "")
        ]
    surfaces = list({surface["id"]: surface for surface in surfaces}.values())
    surfaces.sort(key=lambda row: (row["category"], row["component"], row["method"], row["reference"]))
    network_surfaces = [
        surface for surface in surfaces
        if surface["category"] in ("network_service", "url_protocol", "ipc_service")
    ]
    user_surfaces = [
        {
            "id": surface["id"], "category": surface["category"],
            "origin": surface["origin"],
            "signed_component": surface["signed_component"],
            "parser": surface["parser"], "dispatcher": surface["dispatcher"],
            "capability": surface["capability"],
            "prerequisites": ["resident activation", "input delivery path"],
            "missing_links": surface["missing_links"],
            "classification": "UNKNOWN",
            "sources": surface["sources"],
        }
        for surface in surfaces
    ]
    base = {
        "schema_version": 1,
        "tool_version": TOOL_VERSION,
        "generation_command": "python -m analysis_tools.resident_surface_census --root LABEL=<PATH>",
        "input_manifest": manifest,
        "coverage": {
            "archives": archive_count,
            "class_occurrences": class_occurrences,
            "unique_classes": len(models_by_hash),
            "resources": len(resource_records),
            "broad": broad,
        },
        "errors": errors,
    }
    activation = {
        **base,
        "focus_class": focus_class,
        "occurrences": focus_occurrences,
        "distinct_focus_hashes": sorted(set(focus_hashes)),
        "focus_models": [
            {"sha256": digest, **_focus_model(models_by_hash[digest])}
            for digest in sorted(set(focus_hashes))
            if digest in models_by_hash
        ],
        "references": focus_references,
        "dispatch_candidates": focus_dispatch_candidates,
        "nodes": [asdict(focus_nodes[identifier]) for identifier in sorted(relevant)],
        "edges": [
            row for row in focus_edge_rows
            if row["caller"] in relevant or row["callee"] in relevant
        ],
        "context_methods": context_methods,
        "strong_components": strong_components,
        "reverse_paths": reverse_paths,
        "activation_ladder": ladder,
        "unresolved_dispatch": [
            row for row in focus_edge_rows if not row["resolved"]
            if row["caller"] in relevant or row["callee"] in relevant
        ],
    }
    return {
        "activation_call_paths": activation,
        "java_extension_surfaces": {**base, "surfaces": surfaces},
        "network_ipc_endpoints": {**base, "endpoints": network_surfaces},
        "user_controlled_input_surfaces": {**base, "surfaces": user_surfaces},
        "coverage": base["coverage"],
        "errors": errors,
        "focus": {"occurrences": focus_occurrences},
        "surfaces": surfaces,
    }


def write_census_outputs(result: Mapping[str, Any], output_dir: Path) -> None:
    output_dir = Path(output_dir)
    for key, filename in zip(
        (
            "activation_call_paths", "java_extension_surfaces",
            "network_ipc_endpoints", "user_controlled_input_surfaces",
        ),
        OUTPUT_FILENAMES,
    ):
        write_json(output_dir / filename, result[key])


def _root_argument(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("root must be LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not label or not raw_path:
        raise argparse.ArgumentTypeError("root must be LABEL=PATH")
    return label, Path(raw_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=_root_argument)
    parser.add_argument("--focus-class")
    parser.add_argument("--broad", action="store_true")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    roots = dict(args.root)
    if len(roots) != len(args.root):
        parser.error("duplicate root label")
    try:
        result = census_roots(
            roots, focus_class=args.focus_class, broad=args.broad,
        )
        write_census_outputs(result, args.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
