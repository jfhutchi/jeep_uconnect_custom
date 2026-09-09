"""Validate and render the RA4 Android Open Accessory transport evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
NOTES_PATH = Path(__file__).with_name("ra4_aoa_notes.json")
MAX_NOTES_BYTES = 2 * 1024 * 1024

REQUIRED_OUTPUTS = (
    "docs/ra4_aoa_transport.md",
    "docs/ra4_usb_execution_surface.md",
    "docs/ra4_android_usb_ownership.md",
    "docs/ra4_phone_projection_service.md",
    "docs/ra4_aoa_test_plan.md",
    "reports/ra4_aoa/aoa_state_machine.json",
    "reports/ra4_aoa/usb_operation_mapping.json",
    "reports/ra4_aoa/execution_surface.json",
    "reports/ra4_aoa/verification.md",
)

EXECUTION_CLASSIFICATIONS = {
    "PRODUCTION CALLABLE",
    "PRODUCTION INTERNAL",
    "TEST/DIAGNOSTIC",
    "UNREACHABLE",
    "REQUIRES NEW CODE",
    "UNKNOWN",
}
HUB_CLASSIFICATIONS = {
    "PROVED TRANSPARENT",
    "STRONGLY SUPPORTED",
    "BENCH TEST REQUIRED",
    "LIKELY BLOCKER",
    "PROVED BLOCKER",
}
PHASE7_CLASSIFICATIONS = {"A", "B", "C", "D"}
EXPECTED_STATES = (
    "DETECT",
    "GET_PROTOCOL",
    "SEND_IDENTITY",
    "START_ACCESSORY",
    "WAIT_DETACH",
    "WAIT_ACCESSORY",
    "SELECT_INTERFACE",
    "BULK_EXCHANGE",
    "RELEASE",
    "COMPLETE",
)


class ModelError(ValueError):
    """Raised when evidence notes violate the AOA evidence contract."""


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def load_notes(path: Path = NOTES_PATH) -> dict[str, Any]:
    try:
        if path.stat().st_size > MAX_NOTES_BYTES:
            raise ModelError(f"notes exceed {MAX_NOTES_BYTES} bytes")
        value = json.loads(path.read_text(encoding="utf-8"))
    except ModelError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ModelError(f"cannot load notes: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelError("notes root must be an object")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{label} must be a nonempty string")
    return value


def _repo_path(value: Any, label: str) -> PurePosixPath:
    text = _require_text(value, label).replace("\\", "/")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or (path.parts and ":" in path.parts[0]):
        raise ModelError(f"{label} must be repository-relative: {value}")
    return path


def _source_ids(value: Any, known: set[str], label: str) -> None:
    if not isinstance(value, list) or not value:
        raise ModelError(f"{label} needs source_ids")
    unknown = set(value) - known
    if unknown:
        raise ModelError(f"{label} references unknown source: {sorted(unknown)}")


def _validate_sources(
    notes: dict[str, Any], *, root: Path, verify_hashes: bool
) -> set[str]:
    sources = notes.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ModelError("sources must be a nonempty list")
    known: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ModelError("each source must be an object")
        source_id = _require_text(source.get("id"), "source id")
        if source_id in known:
            raise ModelError(f"duplicate source id: {source_id}")
        known.add(source_id)
        kind = source.get("kind")
        if kind == "repository":
            path = _repo_path(source.get("path"), "repository source path")
            digest = source.get("sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                raise ModelError(f"invalid SHA-256 for {source_id}")
            _require_text(source.get("locator"), f"locator for {source_id}")
            if verify_hashes:
                resolved = root.joinpath(*path.parts)
                if not resolved.is_file():
                    raise ModelError(f"repository source is missing: {path}")
                actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
                if actual != digest.lower():
                    raise ModelError(
                        f"SHA-256 mismatch for {path}: expected {digest}, got {actual}"
                    )
        elif kind == "public":
            for field in ("title", "publisher", "url", "accessed"):
                _require_text(source.get(field), f"{field} for {source_id}")
            if not source["url"].startswith("https://"):
                raise ModelError(f"public source URL must use HTTPS: {source_id}")
        else:
            raise ModelError(f"unknown source kind for {source_id}")
    return known


def _validate_raw_artifacts(notes: dict[str, Any]) -> None:
    artifacts = notes.get("raw_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ModelError("raw_artifacts must be a nonempty list")
    paths: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ModelError("each raw artifact must be an object")
        if artifact.get("corpus") != "RA4_CORPUS":
            raise ModelError("raw artifact corpus must be RA4_CORPUS")
        path = _repo_path(artifact.get("path"), "raw artifact path")
        normalized = path.as_posix()
        if normalized in paths:
            raise ModelError(f"duplicate raw artifact path: {normalized}")
        paths.add(normalized)
        size = artifact.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ModelError(f"raw artifact size must be positive: {normalized}")
        digest = artifact.get("sha256")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest.lower())
        ):
            raise ModelError(f"raw artifact SHA-256 is invalid: {normalized}")
        _require_text(artifact.get("locator"), f"raw artifact locator for {normalized}")


def _validate_aoa(aoa: Any) -> None:
    if not isinstance(aoa, dict):
        raise ModelError("aoa must be an object")
    if aoa.get("protocol_versions") != [1, 2]:
        raise ModelError("AOA protocol versions must be [1, 2]")
    if aoa.get("accessory_vid") != 0x18D1 or aoa.get("accessory_pids") != [
        0x2D00,
        0x2D01,
    ]:
        raise ModelError("AOA accessory VID/PIDs must be 18D1:2D00/2D01")
    if aoa.get("state_machine") != list(EXPECTED_STATES):
        raise ModelError("AOA state machine order is invalid")

    identity = aoa.get("identity")
    if not isinstance(identity, list) or [row.get("index") for row in identity] != list(
        range(6)
    ):
        raise ModelError("AOA identity string order must be indices 0 through 5")
    for row in identity:
        value = _require_text(row.get("value"), "AOA identity value")
        if len(value.encode("utf-8")) + 1 > 256:
            raise ModelError("AOA identity string exceeds 256-byte NUL-terminated limit")

    requests = aoa.get("control_requests")
    if not isinstance(requests, list) or len(requests) != 8:
        raise ModelError("AOA control request list must contain GET, six strings, and START")
    expected = [("GET_PROTOCOL", 0xC0, 51, 0)]
    expected.extend((f"SEND_STRING_{index}", 0x40, 52, index) for index in range(6))
    expected.append(("START_ACCESSORY", 0x40, 53, 0))
    for row, (state, request_type, request, index) in zip(requests, expected):
        if (
            row.get("state"),
            row.get("bmRequestType"),
            row.get("bRequest"),
            row.get("wIndex"),
        ) != (state, request_type, request, index):
            raise ModelError(f"AOA {state} control constants are invalid")
        if row.get("wValue") != 0:
            raise ModelError(f"AOA {state} wValue must be zero")
        if not isinstance(row.get("timeout_ms"), int) or row["timeout_ms"] <= 0:
            raise ModelError(f"AOA {state} timeout must be positive")
        for field in ("payload", "expected", "failure"):
            _require_text(row.get(field), f"AOA {state} {field}")


def validate_notes(
    notes: dict[str, Any],
    *,
    root: Path = ROOT,
    verify_hashes: bool = True,
) -> None:
    if notes.get("schema_version") != 1:
        raise ModelError("schema_version must be 1")
    baseline = notes.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != (
        "a2daff8c5af6c091c8c199a7e4f75009c47f1169"
    ):
        raise ModelError("baseline must identify the authoritative feasibility commit")

    known_sources = _validate_sources(notes, root=root, verify_hashes=verify_hashes)
    _validate_raw_artifacts(notes)
    _validate_aoa(notes.get("aoa"))

    surfaces = notes.get("execution_surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise ModelError("execution_surfaces must be a nonempty list")
    for surface in surfaces:
        name = _require_text(surface.get("name"), "execution surface name")
        classification = surface.get("classification")
        if classification not in EXECUTION_CLASSIFICATIONS:
            raise ModelError(f"invalid execution classification for {name}")
        for field in (
            "concrete_route",
            "authority_evidence",
            "production_use",
            "permissions",
            "remaining_unknown",
        ):
            _require_text(surface.get(field), f"{field} for {name}")
        if not isinstance(surface.get("operations"), list) or not surface["operations"]:
            raise ModelError(f"operations for {name} must be a nonempty list")
        if not isinstance(surface.get("requires_new_code"), bool):
            raise ModelError(f"requires_new_code for {name} must be boolean")
        if classification == "PRODUCTION CALLABLE":
            authority = surface["authority_evidence"].casefold()
            if any(token in authority for token in ("none", "symbol", "library export")):
                raise ModelError(f"execution authority is not proved for {name}")
        _source_ids(surface.get("source_ids"), known_sources, name)

    mapping = notes.get("operation_mapping")
    if not isinstance(mapping, list) or not mapping:
        raise ModelError("operation_mapping must be a nonempty list")
    for row in mapping:
        operation = _require_text(row.get("aoa_operation"), "AOA operation")
        for field in (
            "ra4_api",
            "implementation",
            "production_use",
            "permissions",
            "remaining_unknown",
        ):
            _require_text(row.get(field), f"{field} for {operation}")
        if not isinstance(row.get("requires_new_code"), bool):
            raise ModelError(f"requires_new_code for {operation} must be boolean")
        _source_ids(row.get("source_ids"), known_sources, operation)

    hub = notes.get("hub")
    if not isinstance(hub, dict) or hub.get("classification") not in HUB_CLASSIFICATIONS:
        raise ModelError("invalid hub classification")
    for field in ("conclusion", "limits"):
        _require_text(hub.get(field), f"hub {field}")
    _source_ids(hub.get("source_ids"), known_sources, "hub")

    ownership = notes.get("ownership")
    if not isinstance(ownership, dict):
        raise ModelError("ownership must be an object")
    for field in ("current_owner", "intercept", "narrowest_change"):
        _require_text(ownership.get(field), f"ownership {field}")
    if not isinstance(ownership.get("lifecycle"), list) or not ownership["lifecycle"]:
        raise ModelError("ownership lifecycle must be a nonempty list")
    _source_ids(ownership.get("source_ids"), known_sources, "ownership")

    projection = notes.get("projection_contract")
    if not isinstance(projection, dict):
        raise ModelError("projection_contract must be an object")
    for field in (
        "phone_projection_service",
        "device_connection_manager",
        "usb_relationship",
        "gateway",
        "expected_owner",
    ):
        _require_text(projection.get(field), f"projection {field}")
    _source_ids(projection.get("source_ids"), known_sources, "projection contract")

    phase7 = notes.get("phase7")
    classification = phase7.get("classification") if isinstance(phase7, dict) else None
    if not isinstance(classification, str) or classification not in PHASE7_CLASSIFICATIONS:
        raise ModelError("Phase-7 classification must be exactly one of A/B/C/D")
    if phase7.get("decided_before_prototype") is not True:
        raise ModelError("Phase-7 decision must be made before prototype implementation")
    if classification == "C" and not str(phase7.get("exact_execution_surface", "")).strip():
        raise ModelError("Phase-7 C requires an exact external mechanism")
    for field in (
        "exact_execution_surface",
        "blocker",
        "external_instrumentation",
        "prototype_policy",
    ):
        _require_text(phase7.get(field), f"Phase-7 {field}")
    _source_ids(phase7.get("source_ids"), known_sources, "Phase-7")

    prototype = notes.get("prototype")
    if not isinstance(prototype, dict):
        raise ModelError("prototype must be an object")
    if not isinstance(prototype.get("target_code"), bool):
        raise ModelError("prototype target_code must be boolean")
    if phase7["classification"] in {"B", "D"} and prototype["target_code"]:
        raise ModelError("Phase-7 B or D forbids target code")
    if phase7["classification"] == "C":
        if prototype["target_code"]:
            raise ModelError("Phase-7 C forbids new target code")
    scope = _require_text(prototype.get("scope"), "prototype scope")
    if "implement android auto protocol" in scope.casefold():
        raise ModelError("Android Auto protocol implementation is forbidden")
    for field in ("kind", "label"):
        _require_text(prototype.get(field), f"prototype {field}")

    success = notes.get("physical_success")
    if not isinstance(success, list) or len(success) != 10:
        raise ModelError("exactly ten physical AOA success criteria are required")
    for row in success:
        _require_text(row.get("criterion"), "physical criterion")
        if not isinstance(row.get("proved"), bool):
            raise ModelError("physical criterion proved must be boolean")
        _require_text(row.get("evidence"), "physical criterion evidence")

    next_objective = notes.get("next_objective")
    if not isinstance(next_objective, dict):
        raise ModelError("model must contain exactly one next objective")
    for field in ("id", "title", "success", "constraints"):
        _require_text(next_objective.get(field), f"next objective {field}")

    test_plan = notes.get("test_plan")
    if not isinstance(test_plan, dict):
        raise ModelError("test_plan must be an object")
    if test_plan.get("frame_limit") != 256:
        raise ModelError("test frame limit must be 256 bytes")
    for field in ("identity", "request_payload", "response_payload", "recovery"):
        _require_text(test_plan.get(field), f"test plan {field}")

    verification = notes.get("verification")
    if not isinstance(verification, dict):
        raise ModelError("verification must be an object")
    for field in (
        "branch",
        "baseline_tests",
        "new_tests",
        "generator_checks",
        "json_parse",
        "diff_check",
        "artifact_hashes",
        "original_checkout",
        "physical_test",
    ):
        _require_text(verification.get(field), f"verification {field}")


def _cell(value: Any) -> str:
    if isinstance(value, bool):
        return "YES" if value else "NO"
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(_cell(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def _sources(notes: dict[str, Any]) -> str:
    lines = ["## Sources", ""]
    for index, source in enumerate(notes["sources"], 1):
        if source["kind"] == "repository":
            detail = (
                f"`{source['path']}` ({source['locator']}), SHA-256 "
                f"`{source['sha256']}`"
            )
        else:
            detail = (
                f"[{source['title']}]({source['url']}), {source['publisher']}, "
                f"accessed {source['accessed']}"
            )
        lines.append(f"{index}. {detail}.")
    return "\n".join(lines)


def _main_report(notes: dict[str, Any]) -> str:
    phase7 = notes["phase7"]
    lines = [
        "# RA4 Android Open Accessory Transport",
        "",
        f"**Phase-7 classification: {phase7['classification']}. Physical AOA transport: NOT PROVED.**",
        "",
        "## Conclusion",
        "",
        phase7["exact_execution_surface"],
        "",
        f"Exact blocker: {phase7['blocker']}",
        "",
        "The recovered host stack is sufficient in principle for AOA control and bulk operations. This is an API-capability conclusion, not execution authority or physical transport proof.",
        "",
        "## Exact AOA control sequence",
        "",
        _table(
            ("State", "bmRequestType", "bRequest", "wValue", "wIndex", "Payload", "Expected", "Timeout", "Failure"),
            [
                (
                    row["state"],
                    f"0x{row['bmRequestType']:02X}",
                    row["bRequest"],
                    row["wValue"],
                    row["wIndex"],
                    row["payload"],
                    row["expected"],
                    f"{row['timeout_ms']} ms",
                    row["failure"],
                )
                for row in notes["aoa"]["control_requests"]
            ],
        ),
        "",
        "After START_ACCESSORY, wait for detach and re-enumeration as `18D1:2D00` or `18D1:2D01`, select configuration 1, claim the first accessory interface's bulk IN/OUT endpoints, exchange only the bounded deterministic test frames, release, and test a clean reconnect.",
        "",
        "## Physical success criteria",
        "",
        _table(
            ("Criterion", "Proved", "Evidence"),
            [(row["criterion"], row["proved"], row["evidence"]) for row in notes["physical_success"]],
        ),
        "",
        "## One next engineering objective",
        "",
        f"**{notes['next_objective']['title'].rstrip('.')}.** "
        f"{notes['next_objective']['success'].rstrip('.')}. Constraints: "
        f"{notes['next_objective']['constraints'].rstrip('.')}.",
        "",
        _sources(notes),
        "",
    ]
    return "\n".join(lines)


def _execution_report(notes: dict[str, Any]) -> str:
    lines = [
        "# RA4 USB Execution Surface",
        "",
        "A library export or a fixed-purpose production caller is not a caller-controlled execution surface. The classifications below preserve that boundary.",
        "",
        _table(
            ("Surface", "Classification", "Operations", "Concrete route", "Production use", "New code", "Permissions", "Remaining unknown"),
            [
                (
                    row["name"], row["classification"], row["operations"],
                    row["concrete_route"], row["production_use"], row["requires_new_code"],
                    row["permissions"], row["remaining_unknown"],
                )
                for row in notes["execution_surfaces"]
            ],
        ),
        "",
        "## Phase-7 decision",
        "",
        f"**{notes['phase7']['classification']}** — {notes['phase7']['blocker']}",
        "",
        f"External instrumentation: {notes['phase7']['external_instrumentation']}",
        "",
        "## Recovered artifact anchors",
        "",
        "All paths are relative to the read-only `RA4_CORPUS` alias; they do not disclose or depend on a local absolute path.",
        "",
        _table(
            ("Path", "Bytes", "SHA-256", "Locator"),
            [
                (row["path"], row["size"], row["sha256"], row["locator"])
                for row in notes["raw_artifacts"]
            ],
        ),
        "",
        _sources(notes),
        "",
    ]
    return "\n".join(lines)


def _ownership_report(notes: dict[str, Any]) -> str:
    ownership = notes["ownership"]
    hub = notes["hub"]
    return "\n".join(
        [
            "# RA4 Android USB Ownership",
            "",
            "## Current owner",
            "",
            ownership["current_owner"],
            "",
            "```text",
            " -> ".join(ownership["lifecycle"]),
            "```",
            "",
            "## AOA interception point",
            "",
            ownership["intercept"],
            "",
            f"Narrowest required ownership change: {ownership['narrowest_change']}",
            "",
            "Google's AOA documentation states that AOA and MTP cannot be active simultaneously. The stock MTP/MTPZ driver must therefore not retain the phone interface across the AOA switch.",
            "",
            "## Cabin media hub",
            "",
            f"**{hub['classification']}.** {hub['conclusion']}",
            "",
            f"Limit: {hub['limits']}",
            "",
            _sources(notes),
            "",
        ]
    )


def _projection_report(notes: dict[str, Any]) -> str:
    contract = notes["projection_contract"]
    return "\n".join(
        [
            "# RA4 Phone Projection Service Contract",
            "",
            "This report covers only the contract's relationship to USB ownership. It does not claim that a projection receiver is installed.",
            "",
            _table(
                ("Element", "Recovered expectation"),
                [
                    ("phoneProjectionService", contract["phone_projection_service"]),
                    ("DeviceConnectionManager", contract["device_connection_manager"]),
                    ("USB relationship", contract["usb_relationship"]),
                    ("Gateway", contract["gateway"]),
                    ("Expected owner", contract["expected_owner"]),
                ],
            ),
            "",
            "The designed insertion point is compatible with a projection backend owning device classification and session status, but no recovered method proves that either dormant destination performs AOA negotiation.",
            "",
            _sources(notes),
            "",
        ]
    )


def _test_plan_report(notes: dict[str, Any]) -> str:
    plan = notes["test_plan"]
    aoa = notes["aoa"]
    return "\n".join(
        [
            "# RA4 AOA Test Plan",
            "",
            "**NOT TARGET VERIFIED.** Phase 7 does not provide an authorized target caller. The executable test harness is a host-only state-machine model.",
            "",
            "## Deterministic parameters",
            "",
            _table(
                ("Parameter", "Value"),
                [
                    ("Identity", plan["identity"]),
                    ("Control timeout", f"{aoa['control_timeout_ms']} ms"),
                    ("Detach/re-enumeration timeout", f"{aoa['reenumeration_timeout_ms']} ms"),
                    ("Maximum frame", f"{plan['frame_limit']} bytes"),
                    ("Request", plan["request_payload"]),
                    ("Response", plan["response_payload"]),
                    ("Recovery", plan["recovery"]),
                ],
            ),
            "",
            "## Physical execution gate",
            "",
            notes["phase7"]["blocker"],
            "",
            "Do not run a physical test until an existing authorized caller or a legitimate native development environment supplies the exact control, ownership, and bulk operations. Passive traces may validate hub behavior but cannot establish RA4-originated AOA negotiation.",
            "",
            _sources(notes),
            "",
        ]
    )


def _verification_report(notes: dict[str, Any]) -> str:
    verification = notes["verification"]
    lines = [
        "# RA4 AOA Verification",
        "",
        f"- Working branch: `{verification['branch']}`.",
        f"- Baseline suite: {verification['baseline_tests']}.",
        f"- New tests: {verification['new_tests']}.",
        f"- Generated-report checks: {verification['generator_checks']}.",
        f"- JSON parse: {verification['json_parse']}.",
        f"- Diff check: {verification['diff_check']}.",
        f"- Recovered artifact hashes: {verification['artifact_hashes']}.",
        f"- Original dirty checkout: {verification['original_checkout']}.",
        f"- Physical test: {verification['physical_test']}.",
        "- Firmware, signing, trust, AMS/DRM, vehicle configuration, and vehicle buses: not modified or bypassed.",
        "- Android Auto projection protocol: not implemented.",
        "",
    ]
    return "\n".join(lines)


def render_outputs(
    notes: dict[str, Any], *, root: Path = ROOT
) -> dict[str, bytes]:
    validate_notes(notes, root=root, verify_hashes=False)
    execution_json = {
        "execution_surfaces": notes["execution_surfaces"],
        "hub": notes["hub"],
        "phase7": notes["phase7"],
        "raw_artifacts": notes["raw_artifacts"],
    }
    return {
        "docs/ra4_aoa_transport.md": _main_report(notes).encode("utf-8"),
        "docs/ra4_usb_execution_surface.md": _execution_report(notes).encode("utf-8"),
        "docs/ra4_android_usb_ownership.md": _ownership_report(notes).encode("utf-8"),
        "docs/ra4_phone_projection_service.md": _projection_report(notes).encode("utf-8"),
        "docs/ra4_aoa_test_plan.md": _test_plan_report(notes).encode("utf-8"),
        "reports/ra4_aoa/aoa_state_machine.json": canonical_json(notes["aoa"]),
        "reports/ra4_aoa/usb_operation_mapping.json": canonical_json(notes["operation_mapping"]),
        "reports/ra4_aoa/execution_surface.json": canonical_json(execution_json),
        "reports/ra4_aoa/verification.md": _verification_report(notes).encode("utf-8"),
    }


def write_outputs(outputs: dict[str, bytes], *, root: Path = ROOT) -> None:
    for relative, content in outputs.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def check_outputs(outputs: dict[str, bytes], *, root: Path = ROOT) -> list[str]:
    return [
        relative
        for relative, content in outputs.items()
        if not (root / relative).is_file() or (root / relative).read_bytes() != content
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes", type=Path, default=NOTES_PATH)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    notes = load_notes(args.notes)
    validate_notes(notes, root=ROOT, verify_hashes=True)
    outputs = render_outputs(notes)
    if args.check:
        stale = check_outputs(outputs)
        if stale:
            raise ModelError("generated outputs are stale: " + ", ".join(stale))
        return 0
    write_outputs(outputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
