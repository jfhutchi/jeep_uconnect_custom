"""Hash-bound, read-only extraction for the KIM19 observation model.

The adjacent notes file is a reviewed interpretation, not a reachability solver.
Only selected methods are emitted; the API census scans every selected class.
Vendor bytecode is parsed or disassembled by javap, never loaded or executed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

from analysis_tools.java_classfile import parse_class
from analysis_tools.resident_surface_census import parse_properties
from analysis_tools.target_production_index import build_inventory, resolve_part


LABELS = {"PROVED", "INFERRED", "UNKNOWN", "TARGET OBSERVATION REQUIRED"}
NOTES = Path(__file__).with_name("kim19_runtime_notes.json")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def parse_show_conditions(value: str) -> list[dict]:
    """Strict extraction of the recovered descriptor subset, not native execution.

    Reject malformed/duplicate predicates rather than emulate native recovery.
    Missing PPS attributes are deliberately not assigned a truth value here.
    """
    if not value:
        return []
    result = []
    seen = set()
    for item in value.split(","):
        match = re.fullmatch(r"(/pps/can/[^:,{};]+):([0-9]+|\{[0-9]+(?:;[0-9]+)*\})", item)
        if not match or match[1] in seen:
            raise ValueError("unsupported or duplicate show condition")
        seen.add(match[1])
        result.append({"attribute": match[1], "accepted_strings": match[2].strip("{}").split(";")})
    return result


def known_predicates_match(predicates: list[dict], pps: dict[str, str]) -> bool | None:
    """Only model the all-attributes-present case; None means unresolved.

    Native missing-attribute control flow is not a simple fail-closed AND.
    """
    if any(p["attribute"] not in pps for p in predicates):
        return None
    return all(pps[p["attribute"]] in p["accepted_strings"] for p in predicates)


def network_categories(owner: str, name: str = "") -> list[str]:
    text = owner.lower()
    rules = {
        "java_net": owner.startswith("java/net/"),
        "server_socket": "serversocket" in text,
        "socket": bool(re.search(r"(?:^|/)(?:ssl)?socket(?:factory)?$", text)),
        "datagram": "datagramsocket" in text,
        "multicast": "multicastsocket" in text,
        "url_connection": owner.startswith("java/net/") and "url" in text,
        "tls": owner.startswith("javax/net/ssl/") or "ssl" in text,
        "http_client": "http" in text or "webclient" in text,
        "http_server": "httpserver" in text or "serverconnection" in text,
        "mqtt": "mqtt" in text,
        "ixc": "/ixc/" in text or "/rmi/" in text,
        "native_bridge": "svcipc" in text,
        "phone_bluetooth": any(s in text for s in ("bluetooth", "viamobile", "btspp", "phoneapp")),
        "usb_media": "usb" in text or "/media/" in text,
        "wireless_messaging": "wireless/messaging" in text,
        "callback_event": any(s in text for s in ("listener", "callback", "eventbus")),
        "dynamic_class": name in ("forName", "loadClass", "defineClass") or "urlclassloader" in text,
        "reflection": owner.startswith("java/lang/reflect/"),
        "resource": name in ("getResource", "getResourceAsStream"),
        "script": "scriptengine" in text or "javascript" in text or text.startswith("org/luaj/"),
        "native_library": owner in ("java/lang/System", "java/lang/Runtime") and name in ("load", "loadLibrary"),
        "process": owner in ("java/lang/Runtime", "java/lang/ProcessBuilder") and name in ("exec", "start"),
    }
    return sorted(k for k, v in rules.items() if v)


def method_record(model, method, allowed_literals: set[str]) -> dict:
    # Full class hash binds omitted logging/collection boilerplate, too.
    calls = [e for e in method.member_edges if e.opcode.startswith("invoke") and
             not any(s in e.owner for s in ("Logger", "PrintStream", "StringBuilder")) and
             e.owner not in ("java/lang/String", "java/lang/Object")]
    return {"class": model.name, "method": method.name, "descriptor": method.descriptor,
            "calls": [{"bci": e.offset, "owner": e.owner, "name": e.name,
                       "descriptor": e.descriptor} for e in calls],
            "branches": [{"bci": i.offset, "opcode": i.mnemonic, "targets": i.target_offsets}
                         for i in method.instructions if i.target_offsets],
            "numeric_and_exit_instructions": [{"bci": i.offset, "opcode": i.mnemonic, "operands": i.operands}
                for i in method.instructions if i.mnemonic.startswith(("iconst_", "bipush", "sipush"))
                or i.mnemonic in ("return", "ireturn", "areturn", "athrow")],
            "enum_fields": [{"bci": e.offset, "owner": e.owner, "name": e.name}
                            for e in method.member_edges if "Enum" in e.owner and not e.opcode.startswith("invoke")],
            "constants": [{"bci": e.offset, "value": e.value} for e in method.literal_edges
                          if isinstance(e.value, str) and e.value in allowed_literals],
            "handlers": [asdict(h) for h in method.exception_handlers]}


def validate_labels(value: object) -> None:
    if isinstance(value, dict):
        if "label" in value and value["label"] not in LABELS:
            raise ValueError("invalid evidence label")
        for child in value.values():
            validate_labels(child)
    elif isinstance(value, list):
        for child in value:
            validate_labels(child)


def javap_blocks(output: str, class_name: str) -> dict[tuple[str, str], str]:
    """Index javap -s output by method AND descriptor, including constructors."""
    headers = list(re.finditer(r"(?m)^  (\S[^\n]*)\n    descriptor: (\S+)\s*$", output))
    result = {}
    for index, match in enumerate(headers):
        header, descriptor = match.groups()
        if not descriptor.startswith("("):
            continue
        name = header.split("(", 1)[0].split()[-1]
        if name == class_name.replace("/", "."):
            name = "<init>"
        elif header == "static {};":
            name = "<clinit>"
        end = headers[index + 1].start() if index + 1 < len(headers) else len(output)
        result[name, descriptor] = output[match.end():end]
    return result


def build_reports(work: Path, baseline: Path, *, javap: str | None = None) -> dict[str, dict]:
    notes = json.loads(NOTES.read_text(encoding="utf-8"))
    validate_labels(notes)
    xlets = work / "secondary_iso/usr/share/XLETS"
    root = xlets / "kim_packages/KIM19"
    inventory = json.loads((baseline / "package_inventory.json").read_text(encoding="utf-8"))
    current = build_inventory(root)
    if encode(current) != encode(inventory):
        raise ValueError("KIM19 baseline inventory changed")
    identities = []
    for app in current["applications"]:
        jar = next(j for j in current["jars"] if j["artifact"] == app["jar"])
        keys = ("xlet.appId", "xlet.name", "xlet.version", "xlet.mainClass")
        if any(app["properties"][key] != jar["embedded_descriptor"].get(key) for key in keys):
            raise ValueError("embedded/external application identity differs")
        identities.append(app["package_identity"])
    previous = json.loads((baseline / "capability_candidates.json").read_text(encoding="utf-8"))
    sources = [(root, row) for row in inventory["manifest"]]
    sources += [(xlets, row) for row in previous["shared_base_manifest"]]
    sources += [(work, row) for row in previous["sources"].values()]

    def verify_sources() -> None:
        for parent, row in sources:
            data = (parent / row["artifact"]).read_bytes()
            if len(data) != row["bytes"] or digest(data) != row["sha256"]:
                raise ValueError("source changed: " + row["artifact"])

    verify_sources()
    resolution = resolve_part(root.parent / "kim_pkg_map.lua", "68224525AM")
    if resolution["selected_package"] != "KIM19" or resolution["fallback_used"]:
        raise ValueError("target resolution changed")
    selections = notes["method_selections"]
    allowed = set(notes["allowed_literals"])
    evidence, census, activation, independent, resources = [], [], [], [], []
    for app in inventory["applications"]:
        identity = app["package_identity"]
        annotations = notes["applications"][identity]
        activation.append({**annotations, **{k: app[k] for k in
            ("package_identity", "name", "version", "main_class", "descriptor", "jar", "properties")},
            "show_predicates": parse_show_conditions(app["properties"].get("xlet.showConditions", "")),
            "registered_on_target": "UNKNOWN", "label": "PROVED"})
    # Includes key.jar and all other selected archives, not just the nine main JARs.
    for jar in inventory["jars"]:
        path = root / jar["artifact"]
        app = next((a for a in inventory["applications"] if a["jar"] == jar["artifact"]), None)
        wanted = selections.get(app["package_identity"], {}) if app else {}
        matched = set()
        counts = Counter()
        class_refs = Counter()
        sites, natives = [], []
        classes = {}
        with zipfile.ZipFile(path) as archive:
            for member, keys in notes.get("resource_selections", {}).get(app["package_identity"] if app else "", {}).items():
                data = archive.read(member)
                values = parse_properties(data)["values"]
                resources.append({"jar": jar["artifact"], "member": member,
                    "sha256": digest(data), "values": {key: values[key] for key in keys},
                    "label": "PROVED", "scope": "Bundled configuration; current target consumption is separate"})
            for member in sorted(archive.namelist()):
                if not member.endswith(".class"):
                    continue
                data = archive.read(member)
                model = parse_class(data)
                classes[model.name] = model
                references = {model.name, model.super_name, *model.interfaces}
                references.update(e.owner for m in model.methods for e in (*m.member_edges, *m.type_edges))
                descriptors = [f.descriptor for f in model.fields] + [m.descriptor for m in model.methods]
                references.update(r for d in descriptors for r in re.findall(r"L([^;]+);", d))
                for category in {cat for ref in references if ref for cat in network_categories(ref)}:
                    class_refs[category] += 1
                for method in model.methods:
                    if method.is_native:
                        natives.append({"class": model.name, "method": method.name, "descriptor": method.descriptor})
                    for edge in method.member_edges:
                        if not edge.opcode.startswith("invoke"):
                            continue
                        cats = network_categories(edge.owner, edge.name)
                        counts.update(cats)
                        significant = ((edge.name in ("<init>", "accept", "connect", "createSocket", "createServerSocket", "openConnection")
                                        and edge.owner.startswith(("java/net/", "javax/net/"))) or
                                       "native_library" in cats or "process" in cats)
                        if significant:
                            sites.append({"class": model.name, "method": method.name, "descriptor": method.descriptor,
                                          "bci": edge.offset, "owner": edge.owner, "callee": edge.name,
                                          "callee_descriptor": edge.descriptor, "categories": cats})
                    if method.name in wanted.get(model.name, []):
                        matched.add((model.name, method.name))
                        evidence.append({"jar": jar["artifact"], "jar_sha256": digest(path.read_bytes()),
                            "class_sha256": digest(data), **method_record(model, method, allowed)})
        expected = {(c, m) for c, methods in wanted.items() for m in methods}
        if matched != expected:
            raise ValueError("missing evidence methods: " + repr(expected - matched))
        for site in sites:
            site["syntactic_callers"] = [{"class": c.name, "method": m.name, "descriptor": m.descriptor, "bci": e.offset}
                for c in classes.values() for m in c.methods for e in m.member_edges
                if e.opcode.startswith("invoke") and (e.owner, e.name, e.descriptor) ==
                (site["class"], site["method"], site["descriptor"])]
        census.append({"jar": jar["artifact"], "sha256": digest(path.read_bytes()),
                       "invocation_counts": dict(counts), "class_reference_counts": dict(class_refs),
                       "construction_and_transport_sites": sites, "native_methods": natives})
        if javap and app:
            for cls in notes["independent_classes"].get(app["package_identity"], []):
                proc = subprocess.run([javap, "-s", "-c", "-p", "-classpath", str(path), cls.replace("/", ".")],
                                      check=True, capture_output=True, text=True)
                blocks = javap_blocks(proc.stdout, cls)
                # Check each retained invocation against independently decoded BCI and member name.
                checked = 0
                for record in evidence:
                    if record["jar"] != jar["artifact"] or record["class"] != cls:
                        continue
                    block = blocks[record["method"], record["descriptor"]]
                    for call in record["calls"]:
                        name = '"<init>"' if call["name"] == "<init>" else call["name"]
                        pattern = rf'(?m)^\s*{call["bci"]}:\s+invoke[^\n]*[ .]{re.escape(name)}:{re.escape(call["descriptor"])}'
                        if not re.search(pattern, block):
                            raise ValueError("javap mismatch: " + repr(call))
                        checked += 1
                independent.append({"jar": jar["artifact"], "class": cls, "invocations_checked": checked,
                                    "output_sha256": digest(proc.stdout.encode())})
    verify_sources()
    common = {"schema_version": 1, "scope": "Recovered KIM19; target runtime unobserved",
              "notes_sha256": digest(NOTES.read_bytes())}
    reports = {
        "application_activation_matrix": {"applications": activation, "shared_gates": notes["shared_gates"]},
        "yelp_reachability": notes["yelp"],
        "network_capabilities": {"census_scope": "All 19 KIM19 JARs; counts are syntactic, not runtime",
            "census": census, "resources": resources, "candidates": notes["network"], "extensions": notes["extensions"]},
        "background_services": {"services": notes["background"]},
        "observation_inference_matrix": {"observations": notes["observations"]},
        "method_evidence": {"records": evidence, "native_evidence": notes["native_evidence"],
            "source_hashes": previous["sources"], "omissions": "Logging calls and unapproved literals omitted; hashes bind complete source classes."},
        "validation": {"inventory_identical": True, "coverage": current["coverage"],
            "internally_consistent_application_identities": identities,
            "source_records_rechecked_before_and_after": len(sources), "all_19_jar_hashes_unchanged": True,
            "common_base_files_unchanged": len(previous["shared_base_manifest"]),
            "part_resolution": resolution, "independent_javap": independent,
            "target_observation": "TARGET OBSERVATION REQUIRED",
            "verification_scope": "Report regeneration, suite and Git isolation results are recorded in verification.md."},
    }
    return {name: {**common, **body} for name, body in reports.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="Recovered work root (read-only)")
    parser.add_argument("--baseline", type=Path, default=Path("reports/target_production_state"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--javap", help="Optional independent disassembler executable")
    parser.add_argument("--check", action="store_true", help="Compare outputs without writing")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == args.work.resolve() or args.work.resolve() in output.parents:
        parser.error("output must be outside recovered sources")
    reports = build_reports(args.work, args.baseline, javap=args.javap)
    if not args.check:
        output.mkdir(parents=True, exist_ok=True)
    for name, report in reports.items():
        destination = output / (name + ".json")
        data = encode(report)
        if args.check:
            if destination.read_bytes() != data:
                raise ValueError("report differs: " + name)
        else:
            destination.write_bytes(data)
    print(f'{len(reports)} reports {"verified" if args.check else "written"}; recovered sources unchanged')


if __name__ == "__main__":
    main()
