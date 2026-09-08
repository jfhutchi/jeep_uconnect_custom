"""Read-only target preload inventory; metadata is not runtime reachability.

Never loads vendor classes, extracts archives, or emits key/signature payloads.
Member edges are syntactic JVM references, including virtual/interface calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re
import zipfile

from analysis_tools.java_classfile import parse_class
from analysis_tools.resident_surface_census import ScanLimits, parse_properties
from analysis_tools.stock_capability_index import categories, package_selection


def normalize_part(raw: str | None, *, open_succeeded: bool = True) -> str | None:
    """Model xlets.lua fn4's read(10), anchored patterns and substring order.

    This is an independent ASCII model, not execution of the recovered Lua.
    None represents a nil read, distinct from an open failure. Nonmatching
    reads pass through unchanged in the Lua; the target is entirely ASCII.
    """
    if not open_succeeded:
        return "PN ERROR"
    if raw is None:
        return None
    value = raw[:10]
    if re.match(r"^[0-9]{8}[a-zA-Z]{2}", value):
        return value[:8]
    if re.match(r"^[0-9]{9}", value):
        return value[:9]
    return value


def resolve_part(path: Path, raw: str | None) -> dict:
    summary = package_selection(path)  # Reject executable/nonliteral input first.
    normalized = normalize_part(raw)
    matches = []
    # Use the validated assignment line numbers, excluding block comments.
    lines = path.read_text(encoding="utf-8").splitlines()
    for assignment in summary["assignments"]:
        line = lines[assignment["line"] - 1]
        part = re.search(r'kim_pkg_map\["([0-9]+)"\]', line).group(1)
        if part == normalized:
            matches.append({**assignment, "part": part})
    return {"input": raw, "normalized": normalized,
            "selected_package": matches[-1]["package"] if matches else "KIM0",
            "fallback_used": not matches, "matching_assignments": matches,
            "map_sha256": summary["sha256"],
            "scope": "ASCII model of recovered selector, not observation of FRAM"}


def api_categories(owner: str, name: str) -> list[str]:
    result = set(categories(owner, name))
    text = (owner + "/" + name).lower()
    rules = {
        "network": ("java/net/", "javax/net/", "connectionmanager", "connmgr"),
        "usb_media": ("usb", "/media/", "ipod", "mme", "mediaplayer"),
        "bluetooth_via_mobile": ("bluetooth", "viamobile", "btspp", "phoneapp"),
        "wifi": ("wifi", "wlan", "hotspot"),
        "http_https": ("http", "webclient"),
        "mqtt": ("mqtt",),
        "appmanager_svcipc": ("appmanager", "svcipc"),
        "ixc": ("/ixc/",),
        "filesystem": ("java/io/file", "java/nio/file", "fileconnection"),
        "uri_mime_protocol": ("java/net/uri", "java/net/url", "protocolhandler", "mimetype"),
        "factory_provider": ("factory", "serviceprovider", "serviceloader"),
        "event_dispatch": ("listener", "callback", "eventbus", "dispatch", "intent"),
        "html_xml": ("html", "javax/xml", "org/xml",),
        "serialization": ("objectinputstream", "objectoutputstream", "json", "deserialize"),
    }
    for category, markers in rules.items():
        if any(marker in text for marker in markers):
            result.add(category)
    if name in ("getResourceAsStream", "getResource", "getProperty", "load"):
        result.add("configuration_resource_candidate")
    return sorted(result)


def walk_files(root: Path) -> list[Path]:
    if not root.is_dir() or root.is_symlink() or root.is_junction():
        raise ValueError("input must be a real directory")
    result = []
    def fail(error: OSError) -> None:
        raise error
    for current, directories, files in os.walk(root, followlinks=False, onerror=fail):
        for name in directories + files:
            path = Path(current) / name
            if path.is_symlink() or path.is_junction():
                raise ValueError(f"linked input not inventoried: {path}")
            if name in files:
                result.append(path)
    return sorted(result)


def build_inventory(root: Path, limits: ScanLimits | None = None) -> dict:
    limits = limits or ScanLimits()
    limits.validate()
    files = walk_files(root)
    archives = [p for p in files if p.suffix.lower() == ".jar"]
    if len(archives) > limits.max_archives:
        raise ValueError("archive count limit exceeded")
    manifest, jar_rows, applications = [], [], []
    class_count = total_bytes = 0
    for path in files:
        if path.stat().st_size > limits.max_archive_bytes:
            raise ValueError(f"file size limit: {path}")
        data = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        manifest.append({"artifact": rel, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()})
        if path.name == "xlet.properties":
            properties = parse_properties(data)
            values = properties["values"]
            applications.append({"descriptor": rel, "properties": values,
                "duplicates": properties["duplicates"],
                "package_identity": values.get("xlet.appId"),
                "name": values.get("xlet.name"), "version": values.get("xlet.version"),
                "main_class": values.get("xlet.mainClass"),
                "jar": (path.parent / "jars" / values["xlet.jarFile"]).relative_to(root).as_posix(),
                "physical_presence": "PROVED", "registered_on_target": "UNKNOWN",
                "activated_on_target": "UNKNOWN",
                "declared_gates": {k: v for k, v in values.items() if any(
                    s in k.lower() for s in ("condition", "daemon", "headless", "policy", "category"))}})
    for path in archives:
        rel = path.relative_to(root).as_posix()
        classes, resources, sites, policies, resource_references = [], [], [], [], []
        embedded_descriptor = None
        with zipfile.ZipFile(path) as jar:
            resource_names = {i.filename for i in jar.infolist()
                              if not i.is_dir() and not i.filename.endswith(".class")}
            names = set()
            for info in jar.infolist():
                if info.is_dir():
                    continue
                if info.filename in names:
                    raise ValueError(f"duplicate archive member: {rel}!{info.filename}")
                names.add(info.filename)
                total_bytes += info.file_size
                if info.file_size > limits.max_member_bytes or total_bytes > limits.max_total_bytes:
                    raise ValueError(f"member/total size limit: {rel}!{info.filename}")
                data = jar.read(info)
                digest = hashlib.sha256(data).hexdigest()
                if not info.filename.endswith(".class"):
                    resources.append({"member": info.filename, "bytes": len(data), "sha256": digest})
                    if info.filename == "xlet.properties":
                        embedded_descriptor = parse_properties(data)["values"]
                    if info.filename.endswith(".policy"):
                        policies.append({"member": info.filename,
                            "declarations": re.findall(r"permission\s+[^;]+;", data.decode("utf-8"))})
                    continue
                class_count += 1
                if class_count > limits.max_classes:
                    raise ValueError("class count limit exceeded")
                model = parse_class(data)
                classes.append({"name": model.name, "member": info.filename, "sha256": digest,
                    "super": model.super_name, "interfaces": model.interfaces,
                    "lifecycle": [{"name": m.name, "descriptor": m.descriptor, "flags": m.access_flags}
                                  for m in model.methods if m.name in (
                                      "initXlet", "startXlet", "pauseXlet", "destroyXlet")],
                    "test_name_candidate": bool(re.search(r"(?:^|/)(?:test|unittest)|Test(?:Case|Runner|Util|Framework)|Emulator", model.name, re.I))})
                for method in model.methods:
                    for literal in method.literal_edges:
                        if isinstance(literal.value, str) and literal.value.lstrip("/") in resource_names:
                            resource_references.append({"class": model.name, "method": method.name,
                                "caller_descriptor": method.descriptor, "offset": literal.offset,
                                "member": literal.value.lstrip("/"),
                                "claim": "PROVED resource-name literal; consumption requires call/data-flow review"})
                    for edge in method.member_edges:
                        groups = api_categories(edge.owner, edge.name)
                        if groups and edge.opcode.startswith("invoke"):
                            sites.append({"class": model.name, "method": method.name,
                                "caller_descriptor": method.descriptor, "categories": groups,
                                **asdict(edge)})
        jar_rows.append({"artifact": rel, "classes": classes, "resources": resources,
            "embedded_descriptor": embedded_descriptor,
            "resource_name_references": resource_references,
            "declared_permissions": policies, "api_sites": sites,
            "api_counts": dict(sorted(Counter(c for s in sites for c in s["categories"]).items())),
            "configuration_files_consumed": "Resource names and call sites are candidates; traced consumption is in capability_candidates.json.",
            "externally_controlled_input_sources": "UNKNOWN unless linked by a candidate evidence chain",
            "registration_activation": "Physical metadata only; no runtime or automatic dead-code assertion"})
    jar_by_path = {row["artifact"]: row for row in jar_rows}
    for app in applications:
        if app["jar"] not in jar_by_path:
            raise ValueError(f"missing declared application JAR: {app['jar']}")
        models = {c["name"]: c for c in jar_by_path[app["jar"]]["classes"]}
        name = app["main_class"].replace(".", "/")
        if name not in models:
            raise ValueError(f"missing declared main class: {name}")
        app["lifecycle_chain"] = []
        seen = set()
        while name in models:
            if name in seen:
                raise ValueError("cyclic class hierarchy")
            seen.add(name)
            model = models[name]
            app["lifecycle_chain"].append({"class": name, "methods": model["lifecycle"]})
            name = model["super"]
        app["external_superclass_boundary"] = name
    return {"schema_version": 1, "claim": "PROVED physical metadata and syntactic calls only",
        "root_role": root.name, "manifest": manifest, "applications": applications, "jars": jar_rows,
        "coverage": {"files": len(files), "jars": len(archives), "classes": class_count,
                     "uncompressed_member_bytes": total_bytes, "parse_errors": 0}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.resolve()
    if output.is_relative_to(root):
        raise ValueError("output must be outside recovered input")
    result = build_inventory(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
