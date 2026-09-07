"""Validate a curated evidence ledger and render the three required reports."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

from analysis_tools.evidence_model import (
    ACTIVATION_STATES,
    CLASSIFICATIONS,
    json_bytes,
    validate_evidence,
)


REQUIRED_CANDIDATE_FIELDS = {
    "rank", "component", "activation_path", "user_controlled_input",
    "useful_resulting_capability", "prerequisites",
    "evidence_classification", "unresolved_unknowns",
    "new_package_authorization_required",
}
REPORT_FILENAMES = (
    "stock_extension_surface.md",
    "resident_network_services.md",
    "user_controlled_input_surface.md",
)
_PROHIBITED_RECOMMENDATION = re.compile(
    r"\b(?:recommend(?:ed|ation)?|should|use|perform|try)\b.{0,80}"
    r"\b(?:authentication bypass|unsigned install|trust-store modification|"
    r"ams weakening|firmware modification)\b",
    re.IGNORECASE,
)


def _walk(value: Any, location: str = "$"):
    yield location, value
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{location}[{index}]")


def _validate_classified(record: Mapping[str, Any], claim_key: str) -> None:
    validate_evidence({
        "classification": record.get("classification"),
        "claim": record.get(claim_key),
        "sources": record.get("sources"),
    })


def validate_ledger(ledger: Mapping[str, Any]) -> None:
    if ledger.get("schema_version") != 1:
        raise ValueError("unsupported ledger schema_version")
    # Reuse the canonical writer's path rejection without producing a file.
    json_bytes(ledger)
    for location, value in _walk(ledger):
        final_key = location.rsplit(".", 1)[-1].lower()
        if "payload" in final_key or final_key in ("class_bytes", "resource_bytes"):
            raise ValueError(f"payload-shaped field prohibited at {location}")
        if isinstance(value, str) and _PROHIBITED_RECOMMENDATION.search(value):
            raise ValueError(f"prohibited recommendation at {location}")

    socket = ledger.get("socket_command_source")
    if not isinstance(socket, Mapping):
        raise ValueError("socket_command_source must be an object")
    if socket.get("verdict_classification") not in CLASSIFICATIONS:
        raise ValueError("invalid SocketCommandSource verdict classification")
    if not isinstance(socket.get("verdict"), str) or not socket["verdict"]:
        raise ValueError("SocketCommandSource verdict is required")
    ladder = socket.get("activation_ladder")
    if not isinstance(ladder, Mapping) or set(ladder) != set(ACTIVATION_STATES):
        raise ValueError("activation ladder must contain all seven states")
    for state in ACTIVATION_STATES:
        judgment = ladder[state]
        if not isinstance(judgment, Mapping):
            raise ValueError(f"activation state {state} must be an object")
        _validate_classified(judgment, "conclusion")

    candidates = ledger.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 5:
        raise ValueError("ledger must contain exactly five candidates")
    if [candidate.get("rank") for candidate in candidates] != [1, 2, 3, 4, 5]:
        raise ValueError("candidate ranks must be exactly 1 through 5")
    for candidate in candidates:
        missing = REQUIRED_CANDIDATE_FIELDS - set(candidate)
        if missing:
            raise ValueError(f"candidate fields missing: {sorted(missing)}")
        if candidate["evidence_classification"] not in CLASSIFICATIONS:
            raise ValueError("invalid candidate evidence classification")
        if candidate["new_package_authorization_required"] not in (
            "yes", "no", "unknown",
        ):
            raise ValueError("candidate authorization value must be yes/no/unknown")
        validate_evidence({
            "classification": candidate["evidence_classification"],
            "claim": candidate["useful_resulting_capability"],
            "sources": candidate.get("sources", []),
        })
        for key in ("prerequisites", "unresolved_unknowns"):
            if not isinstance(candidate[key], list):
                raise ValueError(f"candidate {key} must be a list")

    for collection, claim_key in (
        (ledger.get("network_endpoints"), "behavior"),
        (ledger.get("input_surfaces"), "capability"),
    ):
        if not isinstance(collection, list):
            raise ValueError("surface collections must be lists")
        for record in collection:
            if not isinstance(record, Mapping):
                raise ValueError("surface record must be an object")
            _validate_classified(record, claim_key)


def _label(classification: str) -> str:
    return f"**{classification}**"


def _join(values: list[str]) -> str:
    return "; ".join(values) if values else "none identified"


def _table_value(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _render_controlling(ledger: Mapping[str, Any]) -> str:
    socket = ledger["socket_command_source"]
    lines = [
        "# Stock extension surface",
        "",
        "## Evidence boundary",
        "",
        "**PROVED** means direct recovered structure or a source-addressed static edge. "
        "**STRONGLY INFERRED** joins direct facts with a stated inference. "
        "**UNKNOWN** means the recovered evidence does not establish the claim.",
        "",
        f"**UNKNOWN** No target/vehicle operations were performed. Static presence is not "
        "reported as executable or externally reachable behavior.",
        "",
        "## Corpus",
        "",
        f"**PROVED** {_table_value(ledger['corpus']['summary'])}. Coverage: "
        f"{_table_value(ledger['corpus']['coverage'])}.",
        "",
        "## SocketCommandSource verdict",
        "",
        f"{_label(socket['verdict_classification'])} {socket['verdict']}",
        "",
        "| Activation state | Classification | Conclusion |",
        "|---|---|---|",
    ]
    for state in ACTIVATION_STATES:
        judgment = socket["activation_ladder"][state]
        lines.append(
            f"| {state.replace('_', ' ').title()} | {judgment['classification']} | "
            f"{_table_value(judgment['conclusion'])} |"
        )
    lines.extend(["", "## Ranked candidate mechanisms", ""])
    for candidate in ledger["candidates"]:
        classification = candidate["evidence_classification"]
        lines.extend([
            f"### Rank {candidate['rank']} - {candidate['component']}",
            "",
            f"{_label(classification)} Component: {candidate['component']}.",
            f"{_label(classification)} Activation path: {candidate['activation_path']}.",
            f"{_label(classification)} User-controlled input: {candidate['user_controlled_input']}.",
            f"{_label(classification)} Useful resulting capability: "
            f"{candidate['useful_resulting_capability']}.",
            f"{_label(classification)} Prerequisites: {_join(candidate['prerequisites'])}.",
            f"**UNKNOWN** Unresolved unknowns: {_join(candidate['unresolved_unknowns'])}.",
            f"{_label(classification)} New-package authorization required: "
            f"{candidate['new_package_authorization_required']}.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _render_network(ledger: Mapping[str, Any]) -> str:
    lines = [
        "# Resident network and IPC services",
        "",
        "Static network/API presence is not proof of bind, registration, execution, "
        "production enablement, or reachability.",
        "",
        "| Component | Endpoint | Classification | Behavior | Unknowns |",
        "|---|---|---|---|---|",
    ]
    for record in ledger["network_endpoints"]:
        lines.append(
            f"| {_table_value(record['component'])} | {_table_value(record['endpoint'])} | "
            f"{record['classification']} | {_table_value(record['behavior'])} | "
            f"{_table_value(_join(record['unknowns']))} |"
        )
    lines.extend([
        "",
        "**UNKNOWN** Unless a row explicitly supplies dynamic evidence, listener execution "
        "and external reachability remain unknown.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _render_inputs(ledger: Mapping[str, Any]) -> str:
    lines = [
        "# User-controlled input surface",
        "",
        "A complete mechanism requires an origin, signed resident component, "
        "parser/dispatcher, and resulting capability. Missing arrows remain explicit.",
        "",
        "| Origin | Signed resident component | Parser/dispatcher | Capability | Classification | Missing links |",
        "|---|---|---|---|---|---|",
    ]
    for record in ledger["input_surfaces"]:
        lines.append(
            f"| {_table_value(record['origin'])} | {_table_value(record['signed_component'])} | "
            f"{_table_value(record['parser_dispatcher'])} | {_table_value(record['capability'])} | "
            f"{record['classification']} | {_table_value(_join(record['missing_links']))} |"
        )
    lines.extend([
        "",
        "**UNKNOWN** Parser or API references without the complete chain are static "
        "presence only.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", delete=False,
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
        ) as stream:
            temporary = stream.name
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def render_reports(ledger: Mapping[str, Any], docs_dir: Path) -> tuple[Path, ...]:
    validate_ledger(ledger)
    docs_dir = Path(docs_dir)
    contents = (
        _render_controlling(ledger), _render_network(ledger),
        _render_inputs(ledger),
    )
    paths = tuple(docs_dir / name for name in REPORT_FILENAMES)
    for path, content in zip(paths, contents):
        _write_text(path, content)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--docs-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        with args.ledger.open("r", encoding="utf-8") as stream:
            ledger = json.load(stream)
        render_reports(ledger, args.docs_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
