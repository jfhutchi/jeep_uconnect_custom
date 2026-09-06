#!/usr/bin/env python3
"""Correlate redacted qnx_media_runtime_probe reports.

The input already contains only controlled marker names and derived metadata.
This tool validates that boundary, groups candidates by subsystem, and emits a
deterministic inspection order. It never opens recovered vendor artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from analysis_tools.qnx_media_runtime_probe import MARKERS

SOURCE_FORMAT = "qnx-media-runtime-evidence-v1"
OUTPUT_FORMAT = "qnx-runtime-correlation-v1"
DEFAULT_MAX_REPORT_BYTES = 64 * 1024 * 1024
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

FAMILY_MARKERS: dict[str, frozenset[str]] = {
    "qnx_lifecycle": frozenset(
        {
            "pps_launcher",
            "pps_app_launcher",
            "pps_navigator",
            "authman",
            "qtqnxcar2",
            "bar_descriptor",
            "qnx_elf_asset",
            "run_native",
            "appinst_manager",
            "qthomescreen",
        }
    ),
    "notifications": frozenset(
        {
            "hmi_notification",
            "libhnm",
            "hnm_handsfree_plugin",
            "hnm_hfp_call_incoming",
            "hnm_event_priorities",
            "pps_bluetooth_handsfree",
            "pps_handsfree",
        }
    ),
    "qnx_audio_voice": frozenset(
        {
            "audio_manager",
            "audio_manager_get_handle",
            "pps_audio_control",
            "pps_audio_router_control",
            "pps_audio_router_status",
            "pps_audio_devices",
            "pps_audio_status",
            "pps_audio_types",
            "pps_audio_voice_status",
            "pps_mediacontroller_control",
            "pps_mediaplayer_control",
            "pps_mediaplayer_phone",
            "pps_mediaplayer_status",
            "io_audio",
            "io_acoustic",
            "pps_bluetooth",
            "nowplaying",
        }
    ),
    "ra4_audio": frozenset(
        {
            "audio_mgr_cmc_config",
            "audio_ctrl_svc",
            "audio_app_source",
            "mm_control",
            "mm_player",
            "mm_renderer",
            "pps_multimedia_renderer",
        }
    ),
    "display_touch": frozenset(
        {
            "libscreen",
            "screen_window_buffers",
            "screen_window_group",
            "screen_join_window_group",
            "screen_property_focus",
            "screen_property_sensitivity",
            "screen_event_mtouch",
            "video_hmi_class",
            "graphics_config",
            "sgx530",
            "libimggles",
            "libpvr2d",
            "pvrsrv",
        }
    ),
    "projection_service": frozenset(
        {
            "phone_projection_service",
            "iphone_projection",
            "servicebroker",
            "modulelink",
            "modulelink_config",
            "device_projection_swf",
            "projection_back_to_car",
            "phone_projection_event",
        }
    ),
    "ra4_app_lifecycle": frozenset(
        {
            "ams_service",
            "app_manager_service",
            "appmanager_javaapps",
            "xlets_directory",
            "xlet_properties",
        }
    ),
    "legacy_apple_transport": frozenset(
        {
            "usblauncher",
            "io_usb_dcd",
            "roleswap_digitalipodout",
            "roleswap_appledevice",
            "iap2",
            "mm_ipod",
            "io_fs_media",
            "itun",
            "libipod",
            "devu_dcd",
            "ulink_ctrl",
            "omap3530_mg",
            "ehci_omap3",
            "pmic_tw4030_cfg",
            "omap_otg_base",
        }
    ),
    "codec_runtime": frozenset(
        {
            "libcodecengine",
            "decodecombo",
            "dsplink",
            "ce_loader",
            "cmem_parameters",
            "ce_audio_decoder",
            "h264",
            "avc_decoder",
            "openmax",
            "libomx",
            "omx_symbol",
            "gstreamer",
            "libgst",
        }
    ),
    "startup": frozenset({"boot_script", "process_starter", "startup_omap"}),
}

HIGH_SIGNAL_MARKERS = frozenset(
    {
        "audio_mgr_cmc_config",
        "audio_ctrl_svc",
        "appmanager_javaapps",
        "boot_script",
        "device_projection_swf",
        "devu_dcd",
        "graphics_config",
        "io_usb_dcd",
        "omap3530_mg",
        "omap_otg_base",
        "pmic_tw4030_cfg",
        "modulelink_config",
        "phone_projection_service",
        "process_starter",
        "projection_back_to_car",
        "roleswap_digitalipodout",
        "servicebroker",
        "usblauncher",
        "video_hmi_class",
        "xlets_directory",
    }
)


def _safe_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("finding path must be a nonempty string")
    if value.startswith("/") or value.startswith("\\") or "\\" in value:
        raise ValueError(f"finding path is not normalized relative POSIX: {value!r}")
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValueError(f"finding path contains an unsafe component: {value!r}")
    if ":" in raw_parts[0]:
        raise ValueError(f"finding path contains a drive or scheme: {value!r}")
    normalized = PurePosixPath(value).as_posix()
    if normalized != value:
        raise ValueError(f"finding path is not normalized: {value!r}")
    return value


def _validated_markers(finding: dict[str, Any]) -> list[str]:
    tags = finding.get("filename_tags", [])
    content = finding.get("content_markers", {})
    if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
        raise ValueError("filename_tags must be a string list")
    if not isinstance(content, dict):
        raise ValueError("content_markers must be an object")
    names = set(tags)
    for name, details in content.items():
        if not isinstance(name, str) or not isinstance(details, dict):
            raise ValueError("invalid content marker entry")
        count = details.get("count")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError(f"marker {name!r} must have a positive integer count")
        names.add(name)
    unknown = sorted(names.difference(MARKERS))
    if unknown:
        raise ValueError(f"report contains unknown markers: {unknown}")
    return sorted(names)


def _file_kind(path: str) -> str:
    name = PurePosixPath(path).name.casefold()
    if name in {"boot.sh", "graphics.conf", "audiomgrcmc.conf", "modulelink.xml"}:
        return "configuration_or_startup"
    if name.endswith((".conf", ".xml", ".sh", ".cfg", ".ini")):
        return "configuration_or_startup"
    if ".so" in name:
        return "shared_library_candidate"
    if name.endswith((".a", ".lib")):
        return "library_candidate"
    return "evidence_file"


def _candidate(root_label: str, finding: dict[str, Any]) -> dict[str, Any]:
    path = _safe_relative_path(finding.get("path"))
    size = finding.get("size")
    digest = finding.get("sha256")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError(f"invalid size for {path}")
    if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
        raise ValueError(f"invalid SHA-256 for {path}")

    markers = _validated_markers(finding)
    marker_set = set(markers)
    families = sorted(
        name for name, members in FAMILY_MARKERS.items() if marker_set.intersection(members)
    )
    if not families:
        raise ValueError(f"no correlation family for markers in {path}")

    rationale: list[str] = []
    high = sorted(marker_set.intersection(HIGH_SIGNAL_MARKERS))
    if high:
        tier = 1
        rationale.append("stock-specific or startup/configuration marker: " + ", ".join(high))
    elif len(families) >= 2:
        tier = 2
        rationale.append("cross-family marker co-occurrence")
    else:
        tier = 3
        rationale.append("single-family evidence")

    kind = _file_kind(path)
    if kind == "configuration_or_startup":
        tier = min(tier, 1)
        rationale.append("configuration or startup filename")

    return {
        "root_label": root_label,
        "path": path,
        "size": size,
        "sha256": digest,
        "file_kind": kind,
        "priority_tier": tier,
        "families": families,
        "markers": markers,
        "rationale": rationale,
    }


def correlate_report(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict) or report.get("format") != SOURCE_FORMAT:
        raise ValueError(f"input format must be {SOURCE_FORMAT}")
    marker_inventory = report.get("markers")
    if marker_inventory != sorted(MARKERS):
        raise ValueError("input marker inventory does not match this correlator")
    roots = report.get("roots")
    if not isinstance(roots, list):
        raise ValueError("roots must be a list")

    candidates: list[dict[str, Any]] = []
    seen_root_labels: set[str] = set()
    for root in roots:
        if not isinstance(root, dict):
            raise ValueError("each root must be an object")
        root_label = root.get("root_label")
        if (
            not isinstance(root_label, str)
            or not root_label
            or "/" in root_label
            or "\\" in root_label
        ):
            raise ValueError("root_label must be a nonempty basename")
        if root_label in seen_root_labels:
            raise ValueError(f"duplicate root_label: {root_label}")
        seen_root_labels.add(root_label)
        findings = root.get("findings")
        if not isinstance(findings, list):
            raise ValueError(f"findings must be a list for root {root_label}")
        seen_paths: set[str] = set()
        for finding in findings:
            if not isinstance(finding, dict):
                raise ValueError(f"finding must be an object for root {root_label}")
            candidate = _candidate(root_label, finding)
            path = str(candidate["path"])
            if path in seen_paths:
                raise ValueError(f"duplicate finding path in {root_label}: {path}")
            seen_paths.add(path)
            candidates.append(candidate)

    candidates.sort(
        key=lambda item: (
            int(item["priority_tier"]),
            -len(item["families"]),
            str(item["root_label"]),
            str(item["path"]),
        )
    )
    family_files = {
        family: sum(family in item["families"] for item in candidates)
        for family in sorted(FAMILY_MARKERS)
    }
    return {
        "format": OUTPUT_FORMAT,
        "source_format": SOURCE_FORMAT,
        "summary": {
            "candidate_files": len(candidates),
            "priority_tier_1": sum(item["priority_tier"] == 1 for item in candidates),
            "cross_family_files": sum(len(item["families"]) >= 2 for item in candidates),
        },
        "family_files": family_files,
        "candidates": candidates,
    }


def load_report(path: Path | None, max_bytes: int = DEFAULT_MAX_REPORT_BYTES) -> Any:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    if path is None:
        payload = sys.stdin.buffer.read(max_bytes + 1)
    else:
        if path.is_symlink():
            raise ValueError(f"refusing symlink report: {path}")
        size = path.stat().st_size
        if size > max_bytes:
            raise ValueError(f"report exceeds max_bytes: {size} > {max_bytes}")
        payload = path.read_bytes()
    if len(payload) > max_bytes:
        raise ValueError(f"report exceeds max_bytes: > {max_bytes}")
    return json.loads(payload.decode("utf-8"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Correlate a redacted QNX runtime evidence report"
    )
    parser.add_argument("report", nargs="?", type=Path, help="probe JSON; omit for stdin")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_REPORT_BYTES)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        report = load_report(args.report, args.max_bytes)
        result = correlate_report(report)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
