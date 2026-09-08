#!/usr/bin/env python3
"""Deterministic Yelp observation classification and report generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(__file__).with_name("yelp_observation_model.json")
REPORT_PATH = ROOT / "reports" / "kim19_runtime_analysis" / "yelp_failure_signatures.json"

ALLOWED_FIELDS = {
    "catalog_scope": {"all_pages", "partial", "unknown"},
    "tile_state": {"absent", "disabled", "enabled", "unknown"},
    "launch_state": {"not_attempted", "immediate_exit", "error", "registration", "home", "unexpected"},
    "search_state": {"not_observed", "failed", "results"},
    "functionality": {"not_observed", "home_or_search", "fully_functional"},
}
OPTIONAL_FIELDS = {
    "screen_text", "yelp_present", "launch_attempted", "splash_seen",
    "first_screen_text", "error_text", "remained_open", "returned_to_apps",
    "registration_prompt", "approx_transition_seconds", "notes",
}
BOOLEAN_DETAIL_FIELDS = {
    "yelp_present", "launch_attempted", "splash_seen", "remained_open",
    "returned_to_apps", "registration_prompt",
}
TEXT_DETAIL_FIELDS = {"screen_text", "first_screen_text", "error_text", "notes"}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def strict_json_loads(text: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"invalid JSON numeric constant: {value}")

    return json.loads(text, parse_constant=reject_constant)


def load_model(path: Path = MODEL_PATH) -> dict[str, Any]:
    model = strict_json_loads(path.read_text(encoding="utf-8"))
    if model.get("labels") != ["PROVED", "INFERRED", "UNKNOWN", "TARGET OBSERVATION REQUIRED"]:
        raise ValueError("model evidence labels are invalid")
    ids = [row["id"] for row in model["failure_signatures"]]
    if len(ids) != len(set(ids)):
        raise ValueError("failure signature IDs must be unique")
    required_signature = {
        "id", "match_strings", "resource", "trigger", "transition",
        "method_evidence", "interpretation", "label",
    }
    for signature in model["failure_signatures"]:
        if set(signature) != required_signature or signature["label"] != "PROVED":
            raise ValueError(f"invalid failure signature: {signature.get('id')}")
        if not signature["match_strings"] or not signature["method_evidence"]:
            raise ValueError(f"unbound failure signature: {signature['id']}")
    required_predicate = {
        "id", "selector", "call_site", "implementation", "field", "role",
        "required_result", "consumer", "label",
    }
    predicates = model["native_predicates"]
    if len({row["id"] for row in predicates}) != len(predicates):
        raise ValueError("native predicate IDs must be unique")
    for predicate in predicates:
        if set(predicate) != required_predicate or predicate["label"] != "PROVED":
            raise ValueError(f"invalid native predicate: {predicate.get('id')}")
        if not predicate["call_site"] or not predicate["consumer"]:
            raise ValueError(f"unbound native predicate: {predicate['id']}")
    if set(model["outcomes"]) != set("ABCDEFGH"):
        raise ValueError("model must define exactly outcomes A through H")
    return model


def verify_source(path: Path, expected_sha256: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"source hash mismatch for {path}: {actual}")


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))


def _validate(observation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(observation, dict):
        raise ValueError("observation must be a JSON object")
    unknown = sorted(set(observation) - set(ALLOWED_FIELDS) - OPTIONAL_FIELDS)
    if unknown:
        raise ValueError(f"unknown field: {unknown[0]}")
    result = {
        "catalog_scope": "unknown",
        "tile_state": "unknown",
        "launch_state": "not_attempted",
        "search_state": "not_observed",
        "functionality": "not_observed",
    }
    for field, choices in ALLOWED_FIELDS.items():
        if field in observation:
            value = observation[field]
            if not isinstance(value, str) or value not in choices:
                raise ValueError(f"invalid {field}: expected one of {sorted(choices)}")
            result[field] = value
    for field in BOOLEAN_DETAIL_FIELDS:
        if field in observation:
            if observation[field] is not None and not isinstance(observation[field], bool):
                raise ValueError(f"{field} must be boolean or null")
            result[field] = observation[field]
    for field in TEXT_DETAIL_FIELDS:
        if field in observation:
            if not isinstance(observation[field], str):
                raise ValueError(f"{field} must be a string")
            result[field] = observation[field]
    if "approx_transition_seconds" in observation:
        value = observation["approx_transition_seconds"]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise ValueError("approx_transition_seconds must be a nonnegative finite number")
        result["approx_transition_seconds"] = value

    present = result.get("yelp_present")
    if present is False and result["tile_state"] not in {"absent", "unknown"}:
        raise ValueError("yelp_present contradicts tile_state")
    if present is True and result["tile_state"] == "absent":
        raise ValueError("yelp_present contradicts tile_state")
    if present is False and result["tile_state"] == "unknown":
        result["tile_state"] = "absent"

    attempted = result.get("launch_attempted")
    if attempted is False and result["launch_state"] != "not_attempted":
        raise ValueError("launch_attempted contradicts launch_state")
    if attempted is True and result["tile_state"] in {"absent", "disabled"}:
        raise ValueError("launch_attempted contradicts tile_state")
    if attempted is True and result["launch_state"] == "not_attempted":
        if result.get("registration_prompt") is True:
            result["launch_state"] = "registration"
        elif result.get("error_text", "").strip():
            result["launch_state"] = "error"
        elif result.get("returned_to_apps") is True or result.get("remained_open") is False:
            result["launch_state"] = "immediate_exit"
        elif result.get("remained_open") is True:
            result["launch_state"] = "home"
        else:
            result["launch_state"] = "unexpected"
    if result.get("registration_prompt") is True and result["launch_state"] != "registration":
        raise ValueError("registration_prompt contradicts launch_state")
    if result.get("returned_to_apps") is True and result.get("remained_open") is True:
        raise ValueError("returned_to_apps contradicts remained_open")
    if "screen_text" not in result:
        parts = [result.get("first_screen_text", ""), result.get("error_text", "")]
        combined = " ".join(part.strip() for part in parts if part.strip())
        if combined:
            result["screen_text"] = combined
    if result["tile_state"] == "absent" and result["launch_state"] != "not_attempted":
        raise ValueError("cannot launch an absent tile")
    if result["tile_state"] == "disabled" and result["launch_state"] != "not_attempted":
        raise ValueError("cannot launch a disabled tile")
    if result["search_state"] != "not_observed" and result["launch_state"] != "home":
        raise ValueError("search observation requires launch_state home")
    if result["functionality"] == "fully_functional" and result["search_state"] != "results":
        raise ValueError("fully_functional requires observed results")
    return result


def _classify(observation: dict[str, Any]) -> str:
    if observation["functionality"] == "fully_functional":
        return "G"
    if observation["launch_state"] == "registration":
        return "E"
    if observation["launch_state"] == "error" or observation["search_state"] == "failed":
        return "D"
    if observation["launch_state"] == "immediate_exit":
        return "C"
    if observation["launch_state"] == "home":
        return "F"
    if observation["tile_state"] == "disabled":
        return "B"
    if observation["tile_state"] == "absent" and observation["catalog_scope"] == "all_pages":
        return "A"
    return "H"


def _matched_signatures(text: str, signatures: list[dict[str, Any]]) -> list[str]:
    normalized = _normalize(text)
    matches = []
    for signature in signatures:
        values = [_normalize(value) for value in signature["match_strings"]]
        if any(value and value in normalized for value in values):
            matches.append(signature["id"])
    return sorted(matches)


def analyze_observation(observation: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    checked = _validate(observation)
    outcome_id = _classify(checked)
    outcome = model["outcomes"][outcome_id]
    matches = _matched_signatures(checked.get("screen_text", ""), model["failure_signatures"])
    return {
        "schema_version": 1,
        "outcome": outcome_id,
        "outcome_name": outcome["name"],
        "observation": checked,
        "matched_failure_signatures": matches,
        "established_facts": outcome["established"],
        "supported_inferences": outcome["supported"],
        "not_established": outcome["not_established"],
        "compatible_hypotheses": outcome["compatible"],
        "incompatible_hypotheses": outcome["incompatible"],
        "remaining_unknowns": outcome["remaining"],
        "next_static_question": outcome["next_static"],
        "next_benign_observation": outcome["next_observation"],
        "evidence_labels": model["labels"],
    }


def build_failure_report(model: dict[str, Any]) -> dict[str, Any]:
    signatures = []
    for source in sorted(model["failure_signatures"], key=lambda row: row["id"]):
        row = dict(source)
        row["visibility_after"] = (
            "The recovered caller shows Yelp/common alert UI; the exact screen "
            "after dismissal remains UNKNOWN unless stated in transition."
        )
        row["returns_to_apps"] = (
            "UNKNOWN; no automatic return to Apps is proved by this signature."
        )
        row["retry_available"] = (
            "No automatic retry is proved. A later ordinary manual action may "
            "be available after dismissal, depending on the retained screen."
        )
        signatures.append(row)
    return {
        "schema_version": 1,
        "scope": model["scope"],
        "evidence_checkpoint": model["evidence_checkpoint"],
        "source_artifacts": model["sources"],
        "model_sha256": hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest(),
        "normalization": "Unicode casefold; retain ASCII letters and digits; collapse other characters to spaces",
        "coverage": (
            "Distinct English packaged Yelp/common user-visible failure texts "
            "reachable from catalog motion lockout, launch UI, touch/VR search, "
            "response-error mapping, and result detail actions; localized "
            "duplicates share the same resource/caller families."
        ),
        "signatures": signatures,
    }


def generate_report(*, check: bool = False) -> int:
    expected = canonical_bytes(build_failure_report(load_model()))
    if check:
        return 0 if REPORT_PATH.exists() and REPORT_PATH.read_bytes() == expected else 1
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_bytes(expected)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated report is stale")
    parser.add_argument("--app-manager", type=Path, help="optional recovered appManager source to hash-check")
    parser.add_argument("--yelp-jar", type=Path, help="optional recovered Yelp JAR source to hash-check")
    args = parser.parse_args(argv)
    model = load_model()
    if args.app_manager:
        verify_source(args.app_manager, model["sources"]["app_manager"]["sha256"])
    if args.yelp_jar:
        verify_source(args.yelp_jar, model["sources"]["yelp_jar"]["sha256"])
    return generate_report(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
