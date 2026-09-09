"""Deterministic synthesis of the completed KIM19 static-capability evidence.

This module does not inspect the radio, contact a service, or execute recovered
code. It verifies committed evidence files by SHA-256, cross-checks their core
invariants, and emits the reviewed final closure model.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NOTES = Path(__file__).with_name("kim19_final_notes.json")
REPORT_NAMES = ("capability_matrix", "handoff_graph", "unresolved_gates")
LABELS = {
    "PROVED",
    "STRONGLY SUPPORTED",
    "INFERRED",
    "UNKNOWN",
    "TARGET OBSERVATION REQUIRED",
}
SURFACE_KEYS = {
    "activation",
    "permissions",
    "registration_catalog",
    "appmanager_ams",
    "ixc",
    "networking",
    "filesystem_storage",
    "usb_sd",
    "phone_bluetooth",
    "navigation_hmi",
    "speech_vr",
    "media",
    "browser_html_script",
    "dynamic_loading",
    "process_native",
    "sockets_listeners",
    "vsb_sdp_broker",
    "inter_application",
    "configuration_extensions",
    "developer_diagnostic",
    "external_data_actions",
}
OBSERVATION_FIELDS = {
    "action",
    "visible_states",
    "proves",
    "falsifies",
    "transmits_data",
    "changes_persistent_state",
    "requires_network",
    "dependencies",
    "stop_condition",
}


def canonical_bytes(value: object) -> bytes:
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


def _unique(rows: list[dict[str, Any]], field: str, what: str) -> set[str]:
    values = [row.get(field) for row in rows]
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{what} requires nonempty {field}")
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {what} {field}")
    return set(values)


def _validate_evidence_refs(
    row: dict[str, Any], evidence_ids: set[str], location: str
) -> None:
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(f"missing evidence at {location}")
    if not set(evidence) <= evidence_ids:
        raise ValueError(f"unknown evidence at {location}")


def _validate_claim(
    claim: object, location: str, evidence_ids: set[str]
) -> None:
    if not isinstance(claim, dict):
        raise ValueError(f"{location} must be a claim object")
    if claim.get("label") not in LABELS:
        raise ValueError(f"invalid label at {location}")
    if not isinstance(claim.get("finding"), str) or not claim["finding"]:
        raise ValueError(f"missing finding at {location}")
    _validate_evidence_refs(claim, evidence_ids, location)


def load_and_validate_notes(
    path: Path = NOTES, *, data: dict[str, Any] | None = None
) -> dict[str, Any]:
    notes = copy.deepcopy(data) if data is not None else json.loads(path.read_text(encoding="utf-8"))
    if notes.get("schema_version") != 1:
        raise ValueError("unsupported notes schema")

    evidence_ids = _unique(notes.get("evidence_inputs", []), "id", "evidence input")
    for row in notes["evidence_inputs"]:
        if not isinstance(row.get("path"), str) or not row["path"]:
            raise ValueError("evidence input requires path")
        digest = row.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("evidence input requires SHA-256")

    id_bound_groups = (
        "ranked_capabilities",
        "dynamic_mechanisms",
        "ixc_services",
        "platform_services",
        "unknowns",
        "observations",
    )
    singleton_keys = (
        "socket_command_source",
        "historical_conditional",
        "ceiling",
        "decision",
    )
    bindings = notes.get("evidence_bindings")
    expected_binding_keys = set(id_bound_groups) | {"scoped_negatives", "singletons"}
    if not isinstance(bindings, dict) or set(bindings) != expected_binding_keys:
        raise ValueError("evidence bindings must cover every summary group")
    for group in id_bound_groups:
        rows = notes.get(group, [])
        row_ids = _unique(rows, "id", group)
        group_bindings = bindings[group]
        if not isinstance(group_bindings, dict) or set(group_bindings) != row_ids:
            raise ValueError(f"evidence bindings do not exactly cover {group}")
        for row in rows:
            row["evidence"] = copy.deepcopy(group_bindings[row["id"]])
            _validate_evidence_refs(row, evidence_ids, f"{group}.{row['id']}")

    negatives = notes.get("scoped_negatives", [])
    negative_bindings = bindings["scoped_negatives"]
    if not isinstance(negative_bindings, list) or len(negative_bindings) != len(negatives):
        raise ValueError("evidence bindings do not exactly cover scoped_negatives")
    for index, (row, evidence) in enumerate(zip(negatives, negative_bindings)):
        row["evidence"] = copy.deepcopy(evidence)
        _validate_evidence_refs(row, evidence_ids, f"scoped_negatives.{index}")

    singleton_bindings = bindings["singletons"]
    if not isinstance(singleton_bindings, dict) or set(singleton_bindings) != set(singleton_keys):
        raise ValueError("evidence bindings do not exactly cover summary singletons")
    for key in singleton_keys:
        notes[key]["evidence"] = copy.deepcopy(singleton_bindings[key])
        _validate_evidence_refs(notes[key], evidence_ids, key)

    defaults = notes.get("surface_defaults", {})
    if set(defaults) != SURFACE_KEYS:
        raise ValueError("surface defaults do not cover exact inventory fields")
    for key, claim in defaults.items():
        _validate_claim(claim, f"surface_defaults.{key}", evidence_ids)

    profiles = notes.get("application_profiles", [])
    if len(profiles) != 9:
        raise ValueError("application profiles must cover nine KIM19 identities")
    _unique(profiles, "identifier", "application profile")
    for profile in profiles:
        overrides = profile.get("surface_overrides", {})
        if not isinstance(overrides, dict) or not set(overrides) <= SURFACE_KEYS:
            raise ValueError("application profile has unknown surface")
        for key, claim in overrides.items():
            _validate_claim(claim, f"{profile['identifier']}.{key}", evidence_ids)

    for group in ("ranked_capabilities", "dynamic_mechanisms", "ixc_services", "platform_services"):
        rows = notes.get(group, [])
        _unique(rows, "id", group)
        for row in rows:
            if row.get("label") not in LABELS:
                raise ValueError(f"invalid label in {group}")
            if "level" in row and row["level"] not in range(6):
                raise ValueError(f"invalid capability level in {group}")

    ladder = notes.get("capability_ladder", [])
    if [row.get("level") for row in ladder] != list(range(6)):
        raise ValueError("capability ladder must define levels zero through five")

    nodes = notes.get("handoff_nodes", [])
    node_ids = _unique(nodes, "id", "handoff node")
    edges = notes.get("handoff_edges", [])
    _unique(edges, "id", "handoff edge")
    for edge in edges:
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            raise ValueError("handoff edge references unknown node")
        if edge.get("label") not in LABELS:
            raise ValueError("invalid label in handoff edge")
        _validate_evidence_refs(edge, evidence_ids, f"handoff_edges.{edge['id']}")

    observations = notes.get("observations", [])
    _unique(observations, "id", "observation")
    if {row.get("category") for row in observations} != set("ABCD"):
        raise ValueError("observations must cover categories A through D")
    for row in observations:
        if row.get("label") != "TARGET OBSERVATION REQUIRED":
            raise ValueError("observation label must be TARGET OBSERVATION REQUIRED")
        if not OBSERVATION_FIELDS <= set(row):
            raise ValueError("observation is missing required safety fields")

    historical = notes.get("historical_conditional", {})
    if historical.get("scope") != "archived KIM1/KIM3/KIM12 only; excluded from KIM19":
        raise ValueError("historical socket scope must remain separate from KIM19")
    if historical.get("level") != 4:
        raise ValueError("historical socket dispatcher is the scoped Level-4 conditional")

    decision = notes.get("decision", {})
    if decision.get("choice") != "B":
        raise ValueError("final project decision must be B")
    if decision.get("completion_status") != "STATIC RESEARCH COMPLETE":
        raise ValueError("missing exact static completion marker")
    return notes


def verify_evidence_inputs(notes: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    loaded: dict[str, Any] = {}
    for row in notes["evidence_inputs"]:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("evidence path must be repository-relative")
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("evidence path must be repository-relative") from exc
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError(f"evidence hash mismatch: {row['id']}")
        loaded[row["id"]] = json.loads(data)
    _cross_check_evidence(loaded)
    return loaded


def _cross_check_evidence(evidence: dict[str, Any]) -> None:
    required = {
        "target_inventory",
        "part_resolution",
        "runtime_activation",
        "runtime_graph",
        "runtime_network",
        "runtime_validation",
        "socket_findings",
        "socket_validation",
        "yelp_handoffs",
        "yelp_gates",
        "performance_export",
        "performance_consumers",
    }
    if set(evidence) != required:
        raise ValueError("evidence input set is incomplete")

    part = evidence["part_resolution"]
    if part.get("selected_package") != "KIM19" or part.get("normalized") != "68224525":
        raise ValueError("part resolution no longer selects KIM19")

    target = evidence["target_inventory"]
    activation = evidence["runtime_activation"]
    if target.get("coverage") != {
        "classes": 4572,
        "files": 37,
        "jars": 19,
        "parse_errors": 0,
        "uncompressed_member_bytes": 50188423,
    }:
        raise ValueError("KIM19 target inventory coverage changed")
    if len(target.get("applications", [])) != 9 or len(target.get("jars", [])) != 19:
        raise ValueError("KIM19 inventory count changed")
    by_id = {row["package_identity"]: row for row in target["applications"]}
    active_by_id = {row["package_identity"]: row for row in activation["applications"]}
    if set(by_id) != set(active_by_id) or len(by_id) != 9:
        raise ValueError("application identities disagree")
    for identifier, row in by_id.items():
        active = active_by_id[identifier]
        for key in ("name", "version", "main_class", "descriptor", "jar"):
            if row[key] != active[key]:
                raise ValueError(f"application metadata disagrees: {identifier} {key}")

    manifest = {row["artifact"]: row for row in target["manifest"]}
    census = evidence["runtime_network"]["census"]
    if len(census) != 19:
        raise ValueError("network census no longer covers 19 JARs")
    for row in census:
        if manifest.get(row["jar"], {}).get("sha256") != row["sha256"]:
            raise ValueError(f"JAR identity disagrees: {row['jar']}")

    validation = evidence["runtime_validation"]
    if not validation.get("all_19_jar_hashes_unchanged") or validation.get("coverage") != target["coverage"]:
        raise ValueError("runtime validation no longer closes source integrity")
    if len(evidence["runtime_graph"].get("edges", [])) != 23:
        raise ValueError("reviewed application service graph changed")

    handoff_ids = {row["id"] for row in evidence["yelp_handoffs"].get("handoffs", [])}
    if not {"h05_phone", "h06_navigation", "h08_negative", "h09_socket_compare"} <= handoff_ids:
        raise ValueError("Yelp receiver or negative closure is missing")

    socket = evidence["socket_findings"].get("primary_verdict", {})
    if (
        socket.get("reachability_category") != 3
        or socket.get("historical_installed_copy_category") != 4
        or socket.get("reason") != "all five copies are in KIM1/KIM3/KIM12; none selected"
    ):
        raise ValueError("SocketCommandSource package-selection verdict changed")
    assertions = evidence["socket_validation"].get("assertions", {})
    if assertions.get("selected_map_contains_socket_packages") is not False or assertions.get("socket_occurrences") != 5:
        raise ValueError("socket validation assertions changed")

    consumers = evidence["performance_consumers"].get("scoped_consumer_result", {})
    if consumers.get("reviewed_exact_candidate_count") != 0:
        raise ValueError("Performance Pages consumer conclusion changed")


def _claim_with_defaults(notes: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    claims = copy.deepcopy(notes["surface_defaults"])
    claims.update(copy.deepcopy(profile.get("surface_overrides", {})))
    if set(claims) != SURFACE_KEYS:
        raise ValueError("expanded application surface is incomplete")
    return claims


def _build_inventory(notes: dict[str, Any], evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    target = evidence["target_inventory"]
    activation = {row["package_identity"]: row for row in evidence["runtime_activation"]["applications"]}
    profiles = {row["identifier"]: row for row in notes["application_profiles"]}
    manifest = {row["artifact"]: row for row in target["manifest"]}
    jars = {row["artifact"]: row for row in target["jars"]}
    network_jars = {row["jar"]: row for row in evidence["runtime_network"]["census"]}

    inventory = []
    for app in sorted(target["applications"], key=lambda row: row["package_identity"].lower()):
        identifier = app["package_identity"]
        if identifier not in profiles:
            raise ValueError(f"missing application profile: {identifier}")
        runtime = activation[identifier]
        primary = manifest[app["jar"]]
        descriptor = manifest[app["descriptor"]]
        policy = jars[app["jar"]].get("declared_permissions", [])
        inventory.append(
            {
                "identifier": identifier,
                "name": app["name"],
                "variant": runtime["variant"],
                "version": app["version"],
                "entry_point": app["main_class"],
                "mode": "daemon/headless" if app["properties"].get("xlet.daemon") == "true" else "GUI/foreground or HMI-started",
                "startup": runtime["startup"],
                "descriptor": {"path": app["descriptor"], "bytes": descriptor["bytes"], "sha256": descriptor["sha256"]},
                "primary_jar": {"path": app["jar"], "bytes": primary["bytes"], "sha256": primary["sha256"]},
                "declared_permissions": policy,
                "descriptor_gates": app["declared_gates"],
                "registered_on_target": app["registered_on_target"],
                "activated_on_target": app["activated_on_target"],
                "highest_supported_level": profiles[identifier]["highest_supported_level"],
                "surfaces": _claim_with_defaults(notes, profiles[identifier]),
            }
        )

    jar_inventory = []
    for path, row in sorted(network_jars.items()):
        jar_inventory.append(
            {
                "path": path,
                "bytes": manifest[path]["bytes"],
                "sha256": row["sha256"],
                "class_entries": len(jars[path].get("classes", [])),
            }
        )
    return inventory, jar_inventory


def build_reports(notes: dict[str, Any], evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inventory, jar_inventory = _build_inventory(notes, evidence)
    notes_sha256 = hashlib.sha256(canonical_bytes(notes)).hexdigest()
    input_hashes = {row["id"]: {"path": row["path"], "sha256": row["sha256"]} for row in notes["evidence_inputs"]}
    common = {
        "schema_version": 1,
        "scope": "Recovered stock-signed KIM19 for part 68224525AM; target runtime unobserved",
        "evidence_inputs": input_hashes,
        "notes_sha256": notes_sha256,
        "notes_hash_encoding": "Canonical sorted ASCII JSON with LF",
    }
    matrix = {
        "capability_ladder": notes["capability_ladder"],
        "kim19_inventory": inventory,
        "jar_inventory": jar_inventory,
        "ranked_capabilities": notes["ranked_capabilities"],
        "ixc_services": notes["ixc_services"],
        "dynamic_mechanisms": notes["dynamic_mechanisms"],
        "platform_services": notes["platform_services"],
        "socket_command_source": notes["socket_command_source"],
        "historical_conditional": notes["historical_conditional"],
        "scoped_negatives": notes["scoped_negatives"],
        "ceiling": notes["ceiling"],
        "decision": notes["decision"],
    }
    graph = {
        "nodes": notes["handoff_nodes"],
        "edges": notes["handoff_edges"],
        "interpretation_rules": notes["handoff_interpretation_rules"],
    }
    gates = {
        "unknowns": notes["unknowns"],
        "observations": notes["observations"],
        "recommended_observation": notes["recommended_observation"],
        "excluded_first_pass_actions": notes["excluded_first_pass_actions"],
        "decision": notes["decision"],
    }
    return {
        "capability_matrix": {**common, **matrix},
        "handoff_graph": {**common, **graph},
        "unresolved_gates": {**common, **gates},
    }


def write_reports(reports: dict[str, dict[str, Any]], output: Path, *, check: bool = False) -> None:
    output = Path(output)
    expected = {f"{name}.json" for name in REPORT_NAMES}
    if set(reports) != set(REPORT_NAMES):
        raise ValueError("report set differs from declared output contract")
    if check:
        actual = {path.name for path in output.glob("*.json")} if output.is_dir() else set()
        missing = expected - actual
        unexpected = actual - expected
        if missing:
            raise ValueError(f"missing report: {sorted(missing)[0]}")
        if unexpected:
            raise ValueError(f"unexpected report: {sorted(unexpected)[0]}")
    else:
        output.mkdir(parents=True, exist_ok=True)
        for path in output.glob("*.json"):
            if path.name not in expected:
                raise ValueError(f"unexpected report: {path.name}")
    for name in REPORT_NAMES:
        path = output / f"{name}.json"
        data = canonical_bytes(reports[name])
        if check:
            if path.read_bytes() != data:
                raise ValueError(f"stale report: {path.name}")
        else:
            path.write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/kim19_final"))
    parser.add_argument("--check", action="store_true", help="verify exact committed report bytes")
    args = parser.parse_args(argv)
    notes = load_and_validate_notes()
    evidence = verify_evidence_inputs(notes)
    reports = build_reports(notes, evidence)
    write_reports(reports, args.output, check=args.check)
    action = "verified" if args.check else "written"
    print(f"{len(reports)} reports {action}; evidence inputs verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
