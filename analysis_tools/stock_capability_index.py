"""Index static capability call sites without executing recovered classes.

Complements resident_surface_census with process/native loading, non-boilerplate
reflection, and incoming references to selected classes. Output is metadata only;
no constant-pool string payloads are emitted. Runtime dispatch is not resolved.
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
from analysis_tools.resident_surface_census import ScanLimits


def package_selection(path: Path) -> dict:
    """Read the shipped literal-only Lua map; never evaluate Lua."""
    data = path.read_bytes()
    values, assignments = {}, []
    in_comment = False
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        line = line.strip()
        if line.startswith("--[["):
            in_comment = True
        if in_comment:
            if "]]" in line:
                in_comment = False
            continue
        if not line or line.startswith("--") or line == "kim_pkg_map = {}":
            continue
        match = re.fullmatch(r'kim_pkg_map\["([0-9]+)"\]\s*=\s*"(KIM[0-9]+)"\s*(?:--.*)?', line)
        if not match:
            raise ValueError(f"unsupported package-map statement at line {number}")
        part, package = match.groups()
        assignments.append({"line": number, "package": package})
        values[part] = package
    if in_comment or not assignments:
        raise ValueError("incomplete or empty package map")
    return {"sha256": hashlib.sha256(data).hexdigest(),
            "assignment_count": len(assignments), "distinct_part_numbers": len(values),
            "effective_package_counts": dict(sorted(Counter(values.values()).items())),
            "assignments": assignments}


def categories(owner: str, name: str) -> list[str]:
    result = []
    if owner == "java/lang/Runtime" and name == "exec" or (
        owner == "java/lang/ProcessBuilder" and name in ("<init>", "start")
    ):
        result.append("process_launch")
    if owner in ("java/lang/Runtime", "java/lang/System") and name in (
        "load", "loadLibrary",
    ):
        result.append("native_library")
    if owner in ("java/lang/ClassLoader", "java/net/URLClassLoader") or (
        owner == "java/lang/Class" and name in ("forName", "newInstance")
    ) or name in ("loadClass", "defineClass", "findClass"):
        result.append("class_loading")
    if owner.startswith("java/lang/reflect/"):
        result.append("reflection")
    if owner.startswith(("java/net/", "javax/net/")) and any(
        token in owner for token in ("Socket", "Datagram")
    ):
        result.append("socket")
    if any(token in owner.lower() for token in (
        "scriptengine", "interpreter", "rhino", "mozilla",
    )) or name in ("eval", "evaluate", "evaluateString"):
        result.append("interpreter_candidate")
    return result


def build_index(root: Path, selected: re.Pattern) -> dict:
    limits = ScanLimits()
    if not root.is_dir():
        raise ValueError("input root must be a directory")
    archives, skipped = [], []

    def fail(error: OSError) -> None:
        raise error

    for current, directories, files in os.walk(root, followlinks=False, onerror=fail):
        parent = Path(current)
        for name in list(directories) + files:
            path = parent / name
            if path.is_symlink() or path.is_junction():
                skipped.append(path.relative_to(root).as_posix())
                if name in directories:
                    directories.remove(name)
            elif name in files and path.suffix.lower() == ".jar":
                archives.append(path)
    archives.sort()
    if len(archives) > limits.max_archives:
        raise ValueError("archive count limit exceeded")
    manifest, models, occurrences = [], {}, {}
    total = count = 0
    for path in archives:
        rel = path.relative_to(root).as_posix()
        if path.stat().st_size > limits.max_archive_bytes:
            raise ValueError(f"archive size limit: {rel}")
        manifest.append({"artifact": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        with zipfile.ZipFile(path) as jar:
            for info in jar.infolist():
                if info.is_dir() or not info.filename.endswith(".class"):
                    continue
                total += info.file_size
                count += 1
                if info.file_size > limits.max_member_bytes or total > limits.max_total_bytes or count > limits.max_classes:
                    raise ValueError(f"class scan limit: {rel}!{info.filename}")
                data = jar.read(info)
                digest = hashlib.sha256(data).hexdigest()
                if digest not in models:
                    models[digest] = parse_class(data)
                occurrences.setdefault(digest, []).append({"artifact": rel, "member": info.filename})
    selected_names = {m.name for m in models.values() if selected.search(m.name)}
    sites, incoming, focus, hierarchy = [], [], [], []
    boilerplate = 0
    for digest, model in sorted(models.items(), key=lambda pair: (pair[1].name, pair[0])):
        source = {"class": model.name, "class_sha256": digest, "occurrences": occurrences[digest]}
        if model.super_name and ("ClassLoader" in model.super_name or model.super_name in selected_names):
            hierarchy.append({**source, "super": model.super_name, "interfaces": model.interfaces})
        if model.name in selected_names:
            focus.append({**source, "super": model.super_name, "interfaces": model.interfaces,
                          "fields": [{"name": f.name, "descriptor": f.descriptor, "flags": f.access_flags}
                                     for f in model.fields],
                          "methods": [{"name": m.name, "descriptor": m.descriptor,
                                       "flags": m.access_flags,
                                       "handlers": [asdict(e) for e in m.exception_handlers]}
                                      for m in model.methods]})
        for method in model.methods:
            caller = {"class_sha256": digest, "class": model.name,
                      "method": method.name, "caller_descriptor": method.descriptor}
            for edge in method.member_edges:
                if edge.owner in selected_names:
                    incoming.append({**caller, **asdict(edge)})
                if not edge.opcode.startswith("invoke"):
                    continue
                groups = categories(edge.owner, edge.name)
                if groups:
                    if method.name == "class$" and edge.owner == "java/lang/Class" and edge.name == "forName":
                        boilerplate += 1
                    else:
                        sites.append({**caller, "categories": groups, **asdict(edge)})
            for edge in method.type_edges:
                if edge.owner in selected_names:
                    incoming.append({**caller, **asdict(edge)})
    package_map = root / "kim_packages/kim_pkg_map.lua"
    selection = package_selection(package_map) if package_map.is_file() else None
    return {"schema_version": 1, "classification": "PROVED",
            "claim": "static structure and syntactic references only; activation and external input are separate",
            "selection_regex": selected.pattern, "skipped": sorted(skipped),
            "coverage": {"archives": len(archives), "class_occurrences": count,
                         "unique_class_hashes": len(models), "uncompressed_class_bytes": total,
                         "omitted_class_dollar_forName_sites": boilerplate},
            "package_selection": selection,
            "junit_class_names": sorted({m.name for m in models.values() if m.name.startswith("junit/")}),
            "manifest": manifest, "class_sources": [
                {"sha256": d, "class": models[d].name, "occurrences": occurrences[d]}
                for d in sorted({s["class_sha256"] for s in sites + incoming})],
            "capability_sites": sites, "incoming_selected": incoming,
            "hierarchy": hierarchy, "selected_classes": focus}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--select", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.resolve()
    if output.is_relative_to(root):
        raise ValueError("output must be outside recovered input root")
    result = build_index(root, re.compile(args.select))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
