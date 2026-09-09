"""Validate and render the RA4 wired-projection feasibility closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
NOTES_PATH = Path(__file__).with_name("wired_projection_notes.json")
MAX_NOTES_BYTES = 2 * 1024 * 1024

EVIDENCE_LEVELS = {
    "PROVED",
    "STRONGLY SUPPORTED",
    "INFERRED",
    "UNKNOWN",
    "TARGET OBSERVATION REQUIRED",
}
ARCHITECTURE_STATUSES = {
    "ALREADY PRESENT",
    "PRESENT BUT NEEDS ADAPTER/GLUE",
    "MISSING SOFTWARE",
    "MISSING HARDWARE",
    "EXTERNAL AUTHENTICATION DEPENDENCY",
    "UNKNOWN",
}
GENERATED_PATHS = (
    "docs/wired_projection_feasibility.md",
    "docs/ra4_usb_architecture.md",
    "docs/ra4_projection_av_pipeline.md",
    "docs/ra4_projection_hmi_integration.md",
    "docs/ra4_vs_later_uconnect_projection.md",
    "docs/carplay_authentication_boundary.md",
    "docs/android_auto_feasibility.md",
    "reports/wired_projection/usb_inventory.json",
    "reports/wired_projection/av_pipeline.json",
    "reports/wired_projection/projection_gap_matrix.json",
    "reports/wired_projection/hardware_comparison.json",
    "reports/wired_projection/verification.md",
)
REQUIRED_MAIN_SECTIONS = (
    "Executive conclusion",
    "RA4 USB architecture",
    "Apple/iAP support",
    "Android/AOA support",
    "Existing projection remnants",
    "Video/display pipeline",
    "Touch/input return path",
    "Audio output path",
    "Microphone path",
    "HMI integration",
    "Media-hub architecture",
    "Later FCA/Harman comparison",
    "CarPlay authentication boundary",
    "Android Auto authentication/protocol boundary",
    "Resource feasibility",
    "Android Auto classification",
    "CarPlay classification",
    "Minimum architecture for each",
    "Exact blockers",
    "One recommended next engineering objective",
    "Verification",
    "Git branch/commit",
)
FORBIDDEN_SCOPE = (
    "restore obsolete 3g",
    "restore yelp networking",
    "bypass mfi",
    "extract authentication secrets",
    "defeat cryptographic checks",
    "implement a projection client",
)


class ModelError(ValueError):
    """Raised when evidence notes violate the closure contract."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_notes(path: Path = NOTES_PATH) -> dict[str, Any]:
    size = path.stat().st_size
    if size > MAX_NOTES_BYTES:
        raise ModelError(f"notes exceed {MAX_NOTES_BYTES} bytes")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ModelError(f"cannot load notes: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelError("notes root must be an object")
    return value


def _require_nonempty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{label} must be a nonempty string")


def _validate_repo_path(path: str) -> Path:
    pure = PurePosixPath(path.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise ModelError(f"repository source path must be repository-relative: {path}")
    return ROOT.joinpath(*pure.parts)


def _all_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True).lower()


def validate_notes(notes: dict[str, Any], *, verify_hashes: bool = True) -> None:
    if notes.get("schema_version") != 1:
        raise ModelError("schema_version must be 1")
    baseline = notes.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != "5b9826b2b6537f12b4bf08a50003ea6914263700":
        raise ModelError("baseline must identify the authoritative KIM19 commit")

    sources = notes.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ModelError("sources must be a nonempty list")
    source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ModelError("each source must be an object")
        source_id = source.get("id")
        _require_nonempty(source_id, "source id")
        if source_id in source_ids:
            raise ModelError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        kind = source.get("kind")
        if kind == "repository":
            path = source.get("path")
            digest = source.get("sha256")
            _require_nonempty(path, "repository source path")
            if not isinstance(digest, str) or len(digest) != 64:
                raise ModelError(f"invalid SHA-256 for {source_id}")
            resolved = _validate_repo_path(path)
            if verify_hashes:
                if not resolved.is_file():
                    raise ModelError(f"repository source is missing: {path}")
                actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
                if actual != digest.lower():
                    raise ModelError(f"SHA-256 mismatch for {path}: expected {digest}, got {actual}")
            _require_nonempty(source.get("locator"), f"locator for {source_id}")
        elif kind == "public":
            for field in ("title", "publisher", "url", "accessed"):
                _require_nonempty(source.get(field), f"{field} for {source_id}")
            if not source["url"].startswith("https://"):
                raise ModelError(f"public source URL must use HTTPS: {source_id}")
        else:
            raise ModelError(f"unknown source kind for {source_id}")

    claims = notes.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ModelError("claims must be a nonempty list")
    claim_ids: set[str] = set()
    for claim in claims:
        claim_id = claim.get("id")
        _require_nonempty(claim_id, "claim id")
        if claim_id in claim_ids:
            raise ModelError(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        if claim.get("level") not in EVIDENCE_LEVELS:
            raise ModelError(f"invalid evidence level for {claim_id}")
        _require_nonempty(claim.get("statement"), f"statement for {claim_id}")
        references = claim.get("source_ids")
        if not isinstance(references, list) or not references:
            raise ModelError(f"claim {claim_id} needs source_ids")
        unknown = set(references) - source_ids
        if unknown:
            raise ModelError(f"claim {claim_id} references unknown source: {sorted(unknown)}")

    negatives = notes.get("negative_searches")
    if not isinstance(negatives, list) or not negatives:
        raise ModelError("negative_searches must be a nonempty list")
    for negative in negatives:
        for field in ("id", "limits", "result"):
            _require_nonempty(negative.get(field), f"negative search {field}")
        if not isinstance(negative.get("roots"), list) or not negative["roots"]:
            raise ModelError("negative search roots must be nonempty")
        if not isinstance(negative.get("terms"), list) or not negative["terms"]:
            raise ModelError("negative search terms must be nonempty")

    next_objective = notes.get("next_objective")
    if not isinstance(next_objective, dict):
        raise ModelError("model must contain exactly one next objective")
    for field in ("id", "title", "success", "constraints"):
        _require_nonempty(next_objective.get(field), f"next objective {field}")

    targets = notes.get("targets")
    if not isinstance(targets, dict) or set(targets) != {"android_auto", "carplay"}:
        raise ModelError("targets must contain android_auto and carplay")
    for target_name, target in targets.items():
        if target.get("grade") not in set("ABCDE"):
            raise ModelError(f"invalid grade for {target_name}")
        architecture = target.get("architecture")
        if not isinstance(architecture, list) or len(architecture) != 7:
            raise ModelError(f"{target_name} architecture must contain seven blocks")
        for block in architecture:
            if block.get("status") not in ARCHITECTURE_STATUSES:
                raise ModelError(f"invalid architecture status for {target_name}: {block.get('status')}")

    for collection_name in ("video", "audio", "microphone", "input"):
        for item in notes.get("av_pipeline", {}).get(collection_name, []):
            if item.get("status") not in ARCHITECTURE_STATUSES:
                raise ModelError(f"invalid AV status in {collection_name}")
            if item.get("evidence") not in claim_ids:
                raise ModelError(f"unknown AV evidence claim: {item.get('evidence')}")

    sections = notes.get("main_sections")
    if not isinstance(sections, list):
        raise ModelError("main_sections must be a list")
    titles = tuple(section.get("title") for section in sections)
    if titles != REQUIRED_MAIN_SECTIONS:
        raise ModelError("main_sections do not match the required ordered section set")
    for section in sections:
        _require_nonempty(section.get("body"), f"body for {section.get('title')}")

    text = _all_text(notes)
    for phrase in FORBIDDEN_SCOPE:
        if phrase in text:
            raise ModelError(f"forbidden scope phrase present: {phrase}")


def _table(headers: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def _source_ledger(notes: dict[str, Any]) -> str:
    lines = ["## Sources", ""]
    for index, source in enumerate(notes["sources"], 1):
        if source["kind"] == "repository":
            location = f"`{source['path']}` ({source['locator']}), SHA-256 `{source['sha256']}`"
        else:
            location = f"[{source['title']}]({source['url']}), {source['publisher']}, accessed {source['accessed']}"
        lines.append(f"{index}. {location}.")
    return "\n".join(lines)


def _claim_ledger(notes: dict[str, Any]) -> str:
    rows = [(claim["id"], claim["level"], claim["statement"], ", ".join(claim["source_ids"])) for claim in notes["claims"]]
    return _table(("Claim", "Level", "Statement", "Sources"), rows)


def _main_report(notes: dict[str, Any]) -> str:
    aa = notes["targets"]["android_auto"]
    cp = notes["targets"]["carplay"]
    lines = [
        "# RA4 Wired Projection Feasibility",
        "",
        f"**Android Auto: {aa['grade']}. CarPlay: {cp['grade']}.**",
        "",
    ]
    for section in notes["main_sections"]:
        lines.extend((f"## {section['title']}", "", section["body"], ""))
        if section["title"] == "Minimum architecture for each":
            for label, target in (("Android Auto", aa), ("CarPlay", cp)):
                lines.extend((f"### {label}", "", _table(("Block", "Status"), [(row["block"], row["status"]) for row in target["architecture"]]), ""))
    lines.extend(("## Evidence ledger", "", _claim_ledger(notes), "", _source_ledger(notes), ""))
    return "\n".join(lines)


def _usb_report(notes: dict[str, Any]) -> str:
    usb = notes["usb_inventory"]
    lines = [
        "# RA4 USB Architecture",
        "",
        "This is a static, read-only architecture closure. It proves a configured USB host stack; it does not claim a working projection receiver.",
        "",
        "## Controller and role",
        "",
        f"- Controller paths: {usb['controller']}",
        f"- Host proof: {usb['host_proof']}",
        f"- Device role: {usb['device_role']}",
        f"- Media hub: {usb['media_hub']}",
        "",
        "## Phone-insertion call graph",
        "",
        "```text",
    ]
    for index, row in enumerate(usb["call_graph"]):
        prefix = "" if index == 0 else "-> "
        lines.append(f"{prefix}{row['stage']}: {row['component']} [{row['status']}]")
    lines.extend(("```", "", "## Class and protocol inventory", "", _table(("Capability", "Status", "Evidence"), [(row["name"], row["status"], row["evidence"]) for row in usb["classes"]]), "", "## Bounded negative searches", ""))
    lines.append(_table(("Search", "Roots", "Terms", "Limits", "Result"), [(row["id"], ", ".join(row["roots"]), ", ".join(row["terms"]), row["limits"], row["result"]) for row in notes["negative_searches"]]))
    lines.extend(("", _source_ledger(notes), ""))
    return "\n".join(lines)


def _av_report(notes: dict[str, Any]) -> str:
    lines = ["# RA4 Projection AV and Input Pipeline", ""]
    for key, title in (("video", "Video/display"), ("audio", "Audio output"), ("microphone", "Microphone/voice input"), ("input", "Touch/button return")):
        lines.extend((f"## {title}", "", _table(("Component", "Status", "Evidence"), [(row["component"], row["status"], row["evidence"]) for row in notes["av_pipeline"][key]]), ""))
    return "\n".join(lines)


def _hmi_report(notes: dict[str, Any]) -> str:
    mechanisms = notes["hmi"]["mechanisms"]
    return "\n".join((
        "# RA4 Projection HMI Integration",
        "",
        "Projection must remain subordinate to stock camera, emergency, display-off, and safety arbitration. No safety bypass is part of this architecture.",
        "",
        "## Existing mechanisms",
        "",
        _table(("Mechanism", "Status", "Evidence"), [(row["component"], row["status"], row["evidence"]) for row in mechanisms]),
        "",
        "## Foreground priority",
        "",
        "```text",
        " > ".join(notes["hmi"]["arbitration"]),
        "```",
        "",
        "Session ownership, visual foreground, audio focus, microphone lease, and input eligibility remain independent state dimensions.",
        "",
    ))


def _comparison_report(notes: dict[str, Any]) -> str:
    return "\n".join((
        "# RA4 Versus Later Uconnect Projection Hardware",
        "",
        "The immediate public Uconnect 4 evidence is a product comparison, not proof of binary or board ancestry. Unknown component identities remain unknown.",
        "",
        _table(("Component", "RA4", "Later projection-capable system", "Confidence"), [(row["component"], row["ra4"], row["later"], row["confidence"]) for row in notes["hardware_comparison"]]),
        "",
        _source_ledger(notes),
        "",
    ))


def _target_report(notes: dict[str, Any], target_name: str) -> str:
    target = notes["targets"][target_name]
    label = "Android Auto" if target_name == "android_auto" else "CarPlay"
    relevant = notes.get("target_sections", {}).get(target_name, [])
    lines = [f"# {label} Feasibility", "", f"**Grade {target['grade']}.** {target['conclusion']}", "", "## Exact blocker", "", target["blocker"], "", "## Minimum architecture", "", _table(("Block", "Status"), [(row["block"], row["status"]) for row in target["architecture"]]), ""]
    for section in relevant:
        lines.extend((f"## {section['title']}", "", section["body"], ""))
    lines.extend((_source_ledger(notes), ""))
    return "\n".join(lines)


def _verification_report(notes: dict[str, Any]) -> str:
    verification = notes["verification"]
    return "\n".join((
        "# Wired Projection Verification",
        "",
        f"- Authoritative base: `{notes['baseline']['commit']}` on `{notes['baseline']['branch']}`.",
        f"- Baseline suite: {verification['baseline_tests']}.",
        f"- Final suite: {verification['final_tests']}.",
        f"- Required generated-report check runs: {verification['check_runs']}.",
        f"- Compile check: {verification['compile_check']}.",
        f"- Diff check: {verification['diff_check']}.",
        f"- Known verification limit: {verification['compiler_limit']}.",
        f"- Original checkout: {verification['original_checkout']}.",
        "- Projection client implementation, firmware writes, radio installation, and vehicle modification: not performed.",
        "- The final commit SHA is reported by Git after commit; generated files intentionally avoid a self-referential hash.",
        "",
    ))


def render_outputs(notes: dict[str, Any]) -> dict[str, bytes]:
    gap = {
        "targets": notes["targets"],
        "next_objective": notes["next_objective"],
        "negative_searches": notes["negative_searches"],
    }
    outputs = {
        "docs/wired_projection_feasibility.md": _main_report(notes).encode("utf-8"),
        "docs/ra4_usb_architecture.md": _usb_report(notes).encode("utf-8"),
        "docs/ra4_projection_av_pipeline.md": _av_report(notes).encode("utf-8"),
        "docs/ra4_projection_hmi_integration.md": _hmi_report(notes).encode("utf-8"),
        "docs/ra4_vs_later_uconnect_projection.md": _comparison_report(notes).encode("utf-8"),
        "docs/carplay_authentication_boundary.md": _target_report(notes, "carplay").encode("utf-8"),
        "docs/android_auto_feasibility.md": _target_report(notes, "android_auto").encode("utf-8"),
        "reports/wired_projection/usb_inventory.json": canonical_json(notes["usb_inventory"]),
        "reports/wired_projection/av_pipeline.json": canonical_json(notes["av_pipeline"]),
        "reports/wired_projection/projection_gap_matrix.json": canonical_json(gap),
        "reports/wired_projection/hardware_comparison.json": canonical_json(notes["hardware_comparison"]),
        "reports/wired_projection/verification.md": _verification_report(notes).encode("utf-8"),
    }
    return {path: payload if payload.endswith(b"\n") else payload + b"\n" for path, payload in outputs.items()}


def write_outputs(outputs: dict[str, bytes]) -> None:
    for relative, payload in outputs.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def check_outputs(outputs: dict[str, bytes]) -> None:
    errors: list[str] = []
    for relative, expected in outputs.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
        elif path.read_bytes() != expected:
            errors.append(f"stale: {relative}")
    report_dir = ROOT / "reports/wired_projection"
    if report_dir.is_dir():
        expected_names = {Path(path).name for path in GENERATED_PATHS if path.startswith("reports/wired_projection/")}
        actual_names = {path.name for path in report_dir.iterdir() if path.is_file()}
        for extra in sorted(actual_names - expected_names):
            errors.append(f"unexpected: reports/wired_projection/{extra}")
    if errors:
        raise ModelError("generated output check failed: " + "; ".join(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="write canonical reports")
    action.add_argument("--check", action="store_true", help="check committed reports")
    args = parser.parse_args(argv)
    try:
        notes = load_notes()
        validate_notes(notes)
        outputs = render_outputs(notes)
        if args.write:
            write_outputs(outputs)
            verb = "wrote"
        else:
            check_outputs(outputs)
            verb = "checked"
    except (ModelError, OSError) as exc:
        parser.error(str(exc))
    manifest = hashlib.sha256(b"".join(outputs[path] for path in sorted(outputs))).hexdigest()
    print(f"{verb} {len(outputs)} files; manifest_sha256={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
