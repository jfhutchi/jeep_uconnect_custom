import copy
import json
import tempfile
import unittest
from pathlib import Path

from analysis_tools.wired_projection_feasibility import (
    ARCHITECTURE_STATUSES,
    GENERATED_PATHS,
    ModelError,
    canonical_json,
    render_outputs,
    validate_notes,
)


def fixture_notes() -> dict:
    evidence_path = "docs/18_omap3730_usb_role_feasibility.md"
    return {
        "schema_version": 1,
        "baseline": {
            "branch": "codex/kim19-final-capability-closure",
            "commit": "5b9826b2b6537f12b4bf08a50003ea6914263700",
        },
        "sources": [
            {
                "id": "repo-usb-role",
                "kind": "repository",
                "title": "OMAP3730 USB role feasibility",
                "path": evidence_path,
                "sha256": "1" * 64,
                "locator": "Decision",
            },
            {
                "id": "google-aoa",
                "kind": "public",
                "title": "Android Open Accessory 1.0",
                "publisher": "Google",
                "url": "https://source.android.com/docs/core/interaction/accessories/aoa",
                "accessed": "2026-09-09",
            },
        ],
        "claims": [
            {
                "id": "usb-host",
                "level": "PROVED",
                "statement": "The recovered image materializes a USB host stack.",
                "source_ids": ["repo-usb-role"],
            },
            {
                "id": "aoa-reference",
                "level": "STRONGLY SUPPORTED",
                "statement": "AOA keeps the accessory in the USB host role.",
                "source_ids": ["google-aoa"],
            },
        ],
        "negative_searches": [
            {
                "id": "projection-backend-negative",
                "roots": ["analysis_ra4_18.45.01/work/hidden_hbc_ifs"],
                "terms": ["androidauto", "libaoa", "io-usb-dcd", "iap2"],
                "limits": "4,110 files; names, ELF dynamic metadata, and controlled raw markers",
                "result": "No named projection receiver or device-function bundle was identified.",
            }
        ],
        "usb_inventory": {
            "controller": "OMAP3730 Mentor and EHCI host backends",
            "host_proof": "io-usb startup plus host HCDs and libusbdi exports",
            "device_role": "UNKNOWN",
            "media_hub": "Active module; exact silicon and reverse-role behavior UNKNOWN",
            "classes": [
                {"name": "mass storage", "status": "ALREADY PRESENT", "evidence": "usb-host"},
                {"name": "AOA", "status": "MISSING SOFTWARE", "evidence": "aoa-reference"},
            ],
            "call_graph": [
                {"stage": "PHONE INSERTION", "component": "cabin media hub", "status": "UNKNOWN"},
                {"stage": "USB ENUMERATION", "component": "io-usb", "status": "ALREADY PRESENT"},
                {"stage": "DEVICE CLASSIFICATION", "component": "enum-usb rules", "status": "ALREADY PRESENT"},
                {"stage": "SERVICE", "component": "projection receiver", "status": "MISSING SOFTWARE"},
                {"stage": "MEDIA/HMI", "component": "projection HMI contract", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
            ],
        },
        "av_pipeline": {
            "video": [{"component": "H.264 decoder", "status": "UNKNOWN", "evidence": "usb-host"}],
            "audio": [{"component": "audioApp to MME", "status": "ALREADY PRESENT", "evidence": "usb-host"}],
            "microphone": [{"component": "application PCM capture", "status": "UNKNOWN", "evidence": "usb-host"}],
            "input": [{"component": "touch events", "status": "PRESENT BUT NEEDS ADAPTER/GLUE", "evidence": "usb-host"}],
        },
        "hmi": {
            "mechanisms": [{"component": "camera preemption", "status": "ALREADY PRESENT", "evidence": "usb-host"}],
            "arbitration": ["camera and critical stock takeover", "projection", "ordinary stock HMI"],
        },
        "hardware_comparison": [
            {"component": "supplier", "ra4": "Harman BE2800", "later": "Panasonic VP4RAC", "confidence": "PROVED"}
        ],
        "targets": {
            "android_auto": {
                "grade": "B",
                "conclusion": "Plausible, with significant software and runtime unknowns.",
                "blocker": "Prove AOA on the stock path.",
                "architecture": [
                    {"block": "PHONE", "status": "ALREADY PRESENT"},
                    {"block": "USB SESSION", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
                    {"block": "PROJECTION PROTOCOL", "status": "MISSING SOFTWARE"},
                    {"block": "VIDEO DECODER / DISPLAY", "status": "UNKNOWN"},
                    {"block": "AUDIO ROUTING", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
                    {"block": "MIC / INPUT RETURN", "status": "UNKNOWN"},
                    {"block": "HMI ARBITRATION", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
                ],
            },
            "carplay": {
                "grade": "C",
                "conclusion": "Additional authenticated Apple transport hardware is not proved present.",
                "blocker": "Identify the MFi authenticator and reversible USB route.",
                "architecture": [
                    {"block": "PHONE", "status": "ALREADY PRESENT"},
                    {"block": "USB SESSION", "status": "UNKNOWN"},
                    {"block": "PROJECTION PROTOCOL", "status": "EXTERNAL AUTHENTICATION DEPENDENCY"},
                    {"block": "VIDEO DECODER / DISPLAY", "status": "UNKNOWN"},
                    {"block": "AUDIO ROUTING", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
                    {"block": "MIC / INPUT RETURN", "status": "UNKNOWN"},
                    {"block": "HMI ARBITRATION", "status": "PRESENT BUT NEEDS ADAPTER/GLUE"},
                ],
            },
        },
        "next_objective": {
            "id": "prove-ra4-aoa",
            "title": "Prove AOA negotiation and bulk I/O through the stock cabin USB path",
            "success": "AOA version response, accessory re-enumeration, and bidirectional bulk frames are observed.",
            "constraints": "Owner-authorized spare/bench system; no vehicle or production-radio modification.",
        },
        "main_sections": [
            {"title": title, "body": f"Evidence-bound section for {title}."}
            for title in (
                "Executive conclusion", "RA4 USB architecture", "Apple/iAP support",
                "Android/AOA support", "Existing projection remnants", "Video/display pipeline",
                "Touch/input return path", "Audio output path", "Microphone path", "HMI integration",
                "Media-hub architecture", "Later FCA/Harman comparison",
                "CarPlay authentication boundary", "Android Auto authentication/protocol boundary",
                "Resource feasibility", "Android Auto classification", "CarPlay classification",
                "Minimum architecture for each", "Exact blockers", "One recommended next engineering objective",
                "Verification", "Git branch/commit",
            )
        ],
        "verification": {
            "baseline_tests": "305 tests passed",
            "final_tests": "311 tests passed with no failures or skips",
            "check_runs": 2,
            "compile_check": "python -m compileall -q analysis_tools exited 0",
            "diff_check": "git diff --check exited 0",
            "compiler_limit": "C arbiter smoke test was unavailable because no C compiler is installed",
            "original_checkout": "fingerprints unchanged",
        },
    }


class WiredProjectionFeasibilityTests(unittest.TestCase):
    def test_model_renders_exact_output_set_and_canonical_json(self):
        notes = fixture_notes()
        validate_notes(notes, verify_hashes=False)
        outputs = render_outputs(notes)
        self.assertEqual(set(outputs), set(GENERATED_PATHS))
        for path, payload in outputs.items():
            self.assertIsInstance(payload, bytes, path)
            self.assertNotIn(b"\r\n", payload, path)
        parsed = json.loads(outputs["reports/wired_projection/projection_gap_matrix.json"])
        self.assertEqual(canonical_json(parsed), outputs["reports/wired_projection/projection_gap_matrix.json"])
        verification = outputs["reports/wired_projection/verification.md"].decode("utf-8")
        self.assertIn("Final suite: 311 tests passed with no failures or skips.", verification)
        self.assertIn("Compile check: python -m compileall -q analysis_tools exited 0.", verification)
        self.assertIn("Diff check: git diff --check exited 0.", verification)
        self.assertIn("Known verification limit: C arbiter smoke test", verification)

    def test_rejects_unknown_architecture_status(self):
        notes = fixture_notes()
        notes["targets"]["android_auto"]["architecture"][0]["status"] = "MAYBE"
        with self.assertRaisesRegex(ModelError, "architecture status"):
            validate_notes(notes, verify_hashes=False)
        self.assertNotIn("MAYBE", ARCHITECTURE_STATUSES)

    def test_rejects_dangling_claim_source_and_unscoped_negative(self):
        notes = fixture_notes()
        notes["claims"][0]["source_ids"] = ["missing"]
        with self.assertRaisesRegex(ModelError, "unknown source"):
            validate_notes(notes, verify_hashes=False)
        notes = fixture_notes()
        notes["negative_searches"][0]["limits"] = ""
        with self.assertRaisesRegex(ModelError, "limits"):
            validate_notes(notes, verify_hashes=False)

    def test_rejects_multiple_next_objectives_and_forbidden_scope(self):
        notes = fixture_notes()
        notes["next_objective"] = [notes["next_objective"], copy.deepcopy(notes["next_objective"])]
        with self.assertRaisesRegex(ModelError, "exactly one next objective"):
            validate_notes(notes, verify_hashes=False)
        notes = fixture_notes()
        notes["main_sections"][0]["body"] = "Restore obsolete 3G connectivity."
        with self.assertRaisesRegex(ModelError, "forbidden scope"):
            validate_notes(notes, verify_hashes=False)

    def test_rejects_absolute_repository_path_and_hash_mismatch(self):
        notes = fixture_notes()
        notes["sources"][0]["path"] = "C:/vendor/image.bin"
        with self.assertRaisesRegex(ModelError, "repository-relative"):
            validate_notes(notes, verify_hashes=False)
        notes = fixture_notes()
        with self.assertRaisesRegex(ModelError, "SHA-256 mismatch"):
            validate_notes(notes, verify_hashes=True)

    def test_main_report_contains_all_required_sections_and_both_grades(self):
        notes = fixture_notes()
        validate_notes(notes, verify_hashes=False)
        report = render_outputs(notes)["docs/wired_projection_feasibility.md"].decode("utf-8")
        for section in notes["main_sections"]:
            self.assertIn(f"## {section['title']}", report)
        self.assertIn("Android Auto: B", report)
        self.assertIn("CarPlay: C", report)


if __name__ == "__main__":
    unittest.main()
