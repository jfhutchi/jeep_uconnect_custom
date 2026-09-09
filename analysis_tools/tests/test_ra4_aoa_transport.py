import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analysis_tools import ra4_aoa_transport as model


def fixture() -> dict:
    source_text = b"evidence\n"
    return {
        "schema_version": 1,
        "baseline": {
            "branch": "codex/ra4-wired-projection-feasibility",
            "commit": "a2daff8c5af6c091c8c199a7e4f75009c47f1169",
        },
        "sources": [
            {
                "id": "repo-evidence",
                "kind": "repository",
                "path": "evidence.txt",
                "sha256": hashlib.sha256(source_text).hexdigest(),
                "locator": "test fixture",
            },
            {
                "id": "google-aoa1",
                "kind": "public",
                "title": "Android Open Accessory 1.0",
                "publisher": "Android Open Source Project / Google",
                "url": "https://source.android.com/docs/core/interaction/accessories/aoa",
                "accessed": "2026-09-09",
            },
        ],
        "raw_artifacts": [
            {
                "corpus": "RA4_CORPUS",
                "path": "hidden_hbc_ifs/segment_001a0000/files/lib/dll/libusbdi.so.2",
                "size": 47302,
                "sha256": "08c1de09a0ea97da4481275dcdf8191efba7208544fee4f6757a57f48f1b3923",
                "locator": "USB host API exports and fixed-purpose import consumers",
            }
        ],
        "aoa": {
            "protocol_versions": [1, 2],
            "accessory_vid": 0x18D1,
            "accessory_pids": [0x2D00, 0x2D01],
            "control_timeout_ms": 1000,
            "reenumeration_timeout_ms": 5000,
            "identity": [
                {"index": 0, "name": "manufacturer", "value": "Owner Lab"},
                {"index": 1, "name": "model", "value": "RA4 AOA Probe"},
                {"index": 2, "name": "description", "value": "Bounded transport test"},
                {"index": 3, "name": "version", "value": "1.0"},
                {"index": 4, "name": "uri", "value": "https://example.invalid/ra4-aoa"},
                {"index": 5, "name": "serial", "value": "RA4-AOA-0001"},
            ],
            "control_requests": [
                {
                    "state": "GET_PROTOCOL",
                    "bmRequestType": 0xC0,
                    "bRequest": 51,
                    "wValue": 0,
                    "wIndex": 0,
                    "payload": "none; device returns two-byte little-endian version",
                    "expected": "protocol version 1 or 2",
                    "timeout_ms": 1000,
                    "failure": "abort and release",
                },
                *[
                    {
                        "state": f"SEND_STRING_{index}",
                        "bmRequestType": 0x40,
                        "bRequest": 52,
                        "wValue": 0,
                        "wIndex": index,
                        "payload": "NUL-terminated UTF-8, at most 256 bytes",
                        "expected": "complete control OUT transfer",
                        "timeout_ms": 1000,
                        "failure": "abort and release",
                    }
                    for index in range(6)
                ],
                {
                    "state": "START_ACCESSORY",
                    "bmRequestType": 0x40,
                    "bRequest": 53,
                    "wValue": 0,
                    "wIndex": 0,
                    "payload": "none",
                    "expected": "complete control OUT then detach",
                    "timeout_ms": 1000,
                    "failure": "abort and release",
                },
            ],
            "state_machine": [
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
            ],
        },
        "execution_surfaces": [
            {
                "name": "libusbdi.so.2",
                "classification": "REQUIRES NEW CODE",
                "operations": ["control", "descriptors", "bulk", "reset", "detach"],
                "concrete_route": "link an authorized native host client",
                "authority_evidence": "none for a new caller",
                "production_use": "stock fixed-purpose clients import subsets",
                "permissions": "io-usb access and exclusive device ownership",
                "requires_new_code": True,
                "remaining_unknown": "new-client authorization and live permissions",
                "source_ids": ["repo-evidence"],
            }
        ],
        "operation_mapping": [
            {
                "aoa_operation": "GET_PROTOCOL",
                "ra4_api": "usbd_setup_vendor + usbd_io",
                "implementation": "libusbdi.so.2",
                "production_use": "vendor requests exist in fixed-purpose clients",
                "requires_new_code": True,
                "permissions": "exclusive device handle",
                "remaining_unknown": "authorized caller",
                "source_ids": ["repo-evidence", "google-aoa1"],
            }
        ],
        "hub": {
            "classification": "STRONGLY SUPPORTED",
            "conclusion": "Host-side USB traffic should traverse the active media hub.",
            "limits": "Exact silicon and physical AOA behavior are unobserved.",
            "source_ids": ["repo-evidence"],
        },
        "ownership": {
            "current_owner": "enum-devices launches io-fs-media/iofs-pfs for MTP/MTPZ",
            "lifecycle": ["attach", "classify", "launch MTP", "claim interface", "release"],
            "intercept": "before the MTP/MTPZ driver launch and interface claim",
            "narrowest_change": "an authorized pre-MTP AOA classifier/owner",
            "source_ids": ["repo-evidence", "google-aoa1"],
        },
        "projection_contract": {
            "phone_projection_service": "receives startProjection(ppId) and emits session events",
            "device_connection_manager": "separate projection-device status owner",
            "usb_relationship": "no USB negotiation method or owner implementation recovered",
            "gateway": "both destinations rejected before invocation or owner subscription",
            "expected_owner": "optional/shared Harman projection backend, exact package unknown",
            "source_ids": ["repo-evidence"],
        },
        "phase7": {
            "classification": "B",
            "decided_before_prototype": True,
            "exact_execution_surface": "No existing callable AOA surface was recovered.",
            "blocker": "No stock-authorized caller accepts the complete AOA control and bulk sequence.",
            "external_instrumentation": "Cannot prove RA4-originated negotiation without such a caller.",
            "prototype_policy": "host model only; no target code",
            "source_ids": ["repo-evidence", "google-aoa1"],
        },
        "physical_success": [
            {"criterion": name, "proved": False, "evidence": "not physically tested"}
            for name in (
                "cabin enumeration",
                "GET_PROTOCOL",
                "START_ACCESSORY",
                "accessory re-enumeration",
                "Google VID/PID",
                "bulk endpoints claimed",
                "RA4-to-phone transmit",
                "phone-to-RA4 transmit",
                "bidirectional deterministic frames",
                "clean detach/reconnect",
            )
        ],
        "prototype": {
            "kind": "HOST_MODEL",
            "target_code": False,
            "label": "NOT TARGET VERIFIED",
            "scope": "AOA transport state machine and bounded mock framing only",
        },
        "test_plan": {
            "identity": "six harmless fixed strings",
            "frame_limit": 256,
            "request_payload": "RA4-AOA-PING",
            "response_payload": "RA4-AOA-PONG",
            "recovery": "release claimed interface and accept a clean reconnect",
        },
        "next_objective": {
            "id": "legitimate-native-environment",
            "title": "Establish a legitimate native development environment on an owner-authorized spare RA4",
            "success": "an authorized host client can execute bounded libusbdi control and bulk operations",
            "constraints": "no bypass, exploit, firmware patch, or trust modification",
        },
        "verification": {
            "branch": "codex/ra4-aoa-transport",
            "baseline_tests": "311 passed",
            "new_tests": "pending final run",
            "generator_checks": "pending final run",
            "json_parse": "pending final run",
            "diff_check": "pending final run",
            "artifact_hashes": "pending final run",
            "original_checkout": "pending final comparison",
            "physical_test": "not performed",
        },
    }


class Ra4AoaTransportModelTests(unittest.TestCase):
    def test_model_renders_exact_required_output_set(self):
        outputs = model.render_outputs(fixture())
        self.assertEqual(set(outputs), set(model.REQUIRED_OUTPUTS))
        for path, content in outputs.items():
            self.assertIsInstance(content, bytes, path)
            self.assertTrue(content.endswith(b"\n"), path)

    def test_renderer_is_deterministic_and_writes_canonical_json(self):
        first = model.render_outputs(fixture())
        second = model.render_outputs(copy.deepcopy(fixture()))
        self.assertEqual(first, second)
        parsed = json.loads(first["reports/ra4_aoa/aoa_state_machine.json"])
        self.assertEqual(parsed["accessory_vid"], 0x18D1)

    def test_repository_sources_are_hash_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evidence.txt").write_bytes(b"evidence\n")
            model.validate_notes(fixture(), root=root)
            (root / "evidence.txt").write_bytes(b"changed\n")
            with self.assertRaisesRegex(model.ModelError, "SHA-256 mismatch"):
                model.validate_notes(fixture(), root=root)

    def test_absolute_repository_path_is_rejected(self):
        notes = fixture()
        notes["sources"][0]["path"] = "C:/private/evidence.txt"
        with self.assertRaisesRegex(model.ModelError, "repository-relative"):
            model.validate_notes(notes, verify_hashes=False)

    def test_raw_artifact_anchors_require_relative_paths_sizes_and_hashes(self):
        notes = fixture()
        notes["raw_artifacts"][0]["path"] = "E:/recovered/libusbdi.so.2"
        with self.assertRaisesRegex(model.ModelError, "raw artifact path"):
            model.validate_notes(notes, verify_hashes=False)

        notes = fixture()
        notes["raw_artifacts"][0]["sha256"] = "unknown"
        with self.assertRaisesRegex(model.ModelError, "raw artifact SHA-256"):
            model.validate_notes(notes, verify_hashes=False)

        notes = fixture()
        notes["raw_artifacts"][0]["size"] = 0
        with self.assertRaisesRegex(model.ModelError, "raw artifact size"):
            model.validate_notes(notes, verify_hashes=False)

    def test_symbol_presence_cannot_be_promoted_to_execution_authority(self):
        notes = fixture()
        notes["execution_surfaces"][0].update(
            classification="PRODUCTION CALLABLE",
            authority_evidence="library exports only",
        )
        with self.assertRaisesRegex(model.ModelError, "execution authority"):
            model.validate_notes(notes, verify_hashes=False)

    def test_phase7_must_be_single_and_decided_before_prototype(self):
        notes = fixture()
        notes["phase7"]["classification"] = ["B", "D"]
        with self.assertRaisesRegex(model.ModelError, "Phase-7"):
            model.validate_notes(notes, verify_hashes=False)
        notes = fixture()
        notes["phase7"]["decided_before_prototype"] = False
        with self.assertRaisesRegex(model.ModelError, "before prototype"):
            model.validate_notes(notes, verify_hashes=False)

    def test_b_or_d_forbids_target_probe_code(self):
        notes = fixture()
        notes["prototype"]["target_code"] = True
        with self.assertRaisesRegex(model.ModelError, "target code"):
            model.validate_notes(notes, verify_hashes=False)

    def test_c_forbids_target_code_and_requires_external_mechanism(self):
        notes = fixture()
        notes["phase7"]["classification"] = "C"
        notes["phase7"]["exact_execution_surface"] = ""
        with self.assertRaisesRegex(model.ModelError, "external mechanism"):
            model.validate_notes(notes, verify_hashes=False)
        notes["phase7"]["exact_execution_surface"] = "passive analyzer"
        notes["prototype"]["target_code"] = True
        with self.assertRaisesRegex(model.ModelError, "target code"):
            model.validate_notes(notes, verify_hashes=False)

    def test_aoa_control_constants_and_string_order_are_locked(self):
        notes = fixture()
        notes["aoa"]["control_requests"][0]["bRequest"] = 50
        with self.assertRaisesRegex(model.ModelError, "GET_PROTOCOL"):
            model.validate_notes(notes, verify_hashes=False)
        notes = fixture()
        notes["aoa"]["identity"][2]["index"] = 5
        with self.assertRaisesRegex(model.ModelError, "identity string order"):
            model.validate_notes(notes, verify_hashes=False)

    def test_accessory_ids_and_success_criteria_are_locked(self):
        notes = fixture()
        notes["aoa"]["accessory_pids"] = [0x2D00, 0x2D05]
        with self.assertRaisesRegex(model.ModelError, "accessory VID/PIDs"):
            model.validate_notes(notes, verify_hashes=False)
        notes = fixture()
        notes["physical_success"].pop()
        with self.assertRaisesRegex(model.ModelError, "ten physical"):
            model.validate_notes(notes, verify_hashes=False)

    def test_unknown_classification_and_dangling_sources_are_rejected(self):
        notes = fixture()
        notes["execution_surfaces"][0]["classification"] = "PRESENT"
        with self.assertRaisesRegex(model.ModelError, "execution classification"):
            model.validate_notes(notes, verify_hashes=False)
        notes = fixture()
        notes["hub"]["source_ids"] = ["missing"]
        with self.assertRaisesRegex(model.ModelError, "unknown source"):
            model.validate_notes(notes, verify_hashes=False)

    def test_projection_protocol_scope_is_rejected(self):
        notes = fixture()
        notes["prototype"]["scope"] = "implement Android Auto protocol messages"
        with self.assertRaisesRegex(model.ModelError, "Android Auto protocol"):
            model.validate_notes(notes, verify_hashes=False)

    def test_exactly_one_next_objective_is_required(self):
        notes = fixture()
        notes["next_objective"] = [notes["next_objective"], notes["next_objective"]]
        with self.assertRaisesRegex(model.ModelError, "one next objective"):
            model.validate_notes(notes, verify_hashes=False)

    def test_write_then_check_detects_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evidence.txt").write_bytes(b"evidence\n")
            outputs = model.render_outputs(fixture(), root=root)
            model.write_outputs(outputs, root=root)
            self.assertEqual(model.check_outputs(outputs, root=root), [])
            target = root / model.REQUIRED_OUTPUTS[0]
            target.write_text("drift\n", encoding="utf-8")
            self.assertEqual(model.check_outputs(outputs, root=root), [model.REQUIRED_OUTPUTS[0]])

    def test_verification_report_requires_and_names_the_working_branch(self):
        notes = fixture()
        notes["verification"].pop("branch")
        with self.assertRaisesRegex(model.ModelError, "verification branch"):
            model.validate_notes(notes, verify_hashes=False)

        rendered = model.render_outputs(fixture())["reports/ra4_aoa/verification.md"]
        self.assertIn(b"codex/ra4-aoa-transport", rendered)


if __name__ == "__main__":
    unittest.main()
