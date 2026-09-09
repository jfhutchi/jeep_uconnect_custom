import json
import unittest

from analysis_tools.qnx_media_runtime_probe import MARKERS
from analysis_tools.qnx_runtime_correlation import correlate_report


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def report_with(findings):
    return {
        "format": "qnx-media-runtime-evidence-v1",
        "markers": sorted(MARKERS),
        "roots": [{"root_label": "hidden_hbc", "findings": findings}],
    }


class CorrelationTests(unittest.TestCase):
    def test_prioritizes_stock_configuration_and_cross_family_candidates(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "usr/bin/nowplaying",
                        "size": 10,
                        "sha256": DIGEST_A,
                        "filename_tags": ["nowplaying"],
                        "content_markers": {},
                    },
                    {
                        "path": "share/audioDSP/audioMgrCMC.conf",
                        "size": 20,
                        "sha256": DIGEST_B,
                        "filename_tags": ["audio_mgr_cmc_config"],
                        "content_markers": {
                            "audio_app_source": {"count": 1, "offsets": [4]}
                        },
                    },
                    {
                        "path": "usr/lib/libprojection.so.1",
                        "size": 30,
                        "sha256": DIGEST_C,
                        "filename_tags": [],
                        "content_markers": {
                            "phone_projection_service": {"count": 1, "offsets": [2]},
                            "screen_join_window_group": {"count": 1, "offsets": [8]},
                            "audio_manager": {"count": 1, "offsets": [12]},
                        },
                    },
                ]
            )
        )
        self.assertEqual(result["format"], "qnx-runtime-correlation-v1")
        self.assertEqual(result["summary"]["candidate_files"], 3)
        self.assertEqual(result["summary"]["priority_tier_1"], 2)
        self.assertEqual(result["summary"]["cross_family_files"], 1)
        self.assertEqual(
            [item["path"] for item in result["candidates"]],
            [
                "usr/lib/libprojection.so.1",
                "share/audioDSP/audioMgrCMC.conf",
                "usr/bin/nowplaying",
            ],
        )
        projection = result["candidates"][0]
        self.assertEqual(projection["priority_tier"], 1)
        self.assertEqual(
            projection["families"],
            ["display_touch", "projection_service", "qnx_audio_voice"],
        )
        self.assertNotIn("offsets", json.dumps(result))

    def test_does_not_copy_uncontrolled_input_fields(self):
        report = report_with(
            [
                {
                    "path": "usr/bin/servicebroker",
                    "size": 1,
                    "sha256": DIGEST_A,
                    "filename_tags": ["servicebroker"],
                    "content_markers": {},
                    "private_vendor_text": "must-not-escape",
                }
            ]
        )
        rendered = json.dumps(correlate_report(report))
        self.assertNotIn("must-not-escape", rendered)
        self.assertIn("servicebroker", rendered)

    def test_rejects_unknown_marker(self):
        report = report_with(
            [
                {
                    "path": "usr/bin/example",
                    "size": 1,
                    "sha256": DIGEST_A,
                    "filename_tags": ["invented_marker"],
                    "content_markers": {},
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "unknown markers"):
            correlate_report(report)

    def test_rejects_unsafe_path(self):
        report = report_with(
            [
                {
                    "path": "../outside",
                    "size": 1,
                    "sha256": DIGEST_A,
                    "filename_tags": ["servicebroker"],
                    "content_markers": {},
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "unsafe component"):
            correlate_report(report)

    def test_rejects_bad_digest_and_marker_count(self):
        bad_digest = report_with(
            [
                {
                    "path": "usr/bin/example",
                    "size": 1,
                    "sha256": "short",
                    "filename_tags": ["servicebroker"],
                    "content_markers": {},
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            correlate_report(bad_digest)

        bad_count = report_with(
            [
                {
                    "path": "usr/bin/example",
                    "size": 1,
                    "sha256": DIGEST_A,
                    "filename_tags": [],
                    "content_markers": {"servicebroker": {"count": 0}},
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "positive integer"):
            correlate_report(bad_count)

    def test_rejects_wrong_format_and_root_label(self):
        with self.assertRaisesRegex(ValueError, "input format"):
            correlate_report({"format": "other", "roots": []})
        with self.assertRaisesRegex(ValueError, "root_label"):
            correlate_report(
                {
                    "format": "qnx-media-runtime-evidence-v1",
                    "markers": sorted(MARKERS),
                    "roots": [{"root_label": "../root", "findings": []}],
                }
            )


    def test_rejects_marker_inventory_drift(self):
        report = report_with([])
        report["markers"] = sorted(MARKERS)[:-1]
        with self.assertRaisesRegex(ValueError, "marker inventory"):
            correlate_report(report)

    def test_rejects_duplicate_root_label_and_finding_path(self):
        duplicate_root = report_with([])
        duplicate_root["roots"].append(
            {"root_label": "hidden_hbc", "findings": []}
        )
        with self.assertRaisesRegex(ValueError, "duplicate root_label"):
            correlate_report(duplicate_root)

        finding = {
            "path": "usr/bin/servicebroker",
            "size": 1,
            "sha256": DIGEST_A,
            "filename_tags": ["servicebroker"],
            "content_markers": {},
        }
        duplicate_path = report_with([finding, dict(finding)])
        with self.assertRaisesRegex(ValueError, "duplicate finding path"):
            correlate_report(duplicate_path)


    def test_correlates_ra4_projection_and_authorized_app_lifecycle(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "share/hmi/DeviceProjection.swf",
                        "size": 30,
                        "sha256": DIGEST_A,
                        "filename_tags": ["device_projection_swf"],
                        "content_markers": {
                            "phone_projection_event": {"count": 1},
                            "app_manager_service": {"count": 1},
                        },
                    }
                ]
            )
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["priority_tier"], 1)
        self.assertEqual(
            candidate["families"],
            ["projection_service", "ra4_app_lifecycle"],
        )


    def test_correlates_legacy_qnx_apple_transport_with_projection(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "etc/usblauncher/rules.lua",
                        "size": 40,
                        "sha256": DIGEST_B,
                        "filename_tags": ["usblauncher"],
                        "content_markers": {
                            "roleswap_digitalipodout": {"count": 1},
                            "phone_projection_service": {"count": 1},
                        },
                    }
                ]
            )
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["priority_tier"], 1)
        self.assertEqual(
            candidate["families"],
            ["legacy_apple_transport", "projection_service"],
        )


    def test_prioritizes_device_controller_runtime_candidate(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "lib/dll/devu-dcd-omap3.so",
                        "size": 50,
                        "sha256": DIGEST_C,
                        "filename_tags": ["devu_dcd"],
                        "content_markers": {
                            "io_usb_dcd": {"count": 1},
                            "ulink_ctrl": {"count": 1},
                            "omap3530_mg": {"count": 1},
                            "pmic_tw4030_cfg": {"count": 1},
                            "omap_otg_base": {"count": 1},
                        },
                    }
                ]
            )
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["priority_tier"], 1)
        self.assertEqual(candidate["families"], ["legacy_apple_transport"])


    def test_prioritizes_qnx6_profile_named_device_controller_candidate(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "lib/dll/devu-usbumass-omap3.so",
                        "size": 60,
                        "sha256": DIGEST_A,
                        "filename_tags": ["devu_usbumass_hw"],
                        "content_markers": {
                            "io_usb_dcd": {"count": 1},
                            "libusbdci": {"count": 1},
                            "usb_device_stack_rule": {"count": 1},
                            "usb_ctrl_pps": {"count": 1},
                            "start_stack_device": {"count": 1},
                        },
                    }
                ]
            )
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["priority_tier"], 1)
        self.assertEqual(candidate["families"], ["legacy_apple_transport"])


    def test_correlates_stock_foreground_policy_with_projection(self):
        result = correlate_report(
            report_with(
                [
                    {
                        "path": "share/hmi/MainSupplement.swf",
                        "size": 70,
                        "sha256": DIGEST_B,
                        "filename_tags": [],
                        "content_markers": {
                            "phone_projection_event": {"count": 1},
                            "foreground_availability": {"count": 1},
                            "phone_incoming_call": {"count": 1},
                            "sms_incoming_message": {"count": 1},
                            "rear_camera_status": {"count": 1},
                            "hvac_popup": {"count": 1},
                        },
                    }
                ]
            )
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["priority_tier"], 1)
        self.assertEqual(
            candidate["families"],
            ["projection_service", "ra4_foreground_policy"],
        )


if __name__ == "__main__":
    unittest.main()
