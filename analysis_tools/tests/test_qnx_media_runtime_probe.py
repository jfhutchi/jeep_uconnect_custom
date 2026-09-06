import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from analysis_tools.qnx_media_runtime_probe import _scan_stream, build_report, scan_root


class StreamTests(unittest.TestCase):
    def test_marker_crossing_chunk_boundary_is_counted_once(self):
        data = b"xxxxlibcodecengine.so and H264"
        digest, matches, consumed = _scan_stream(
            io.BytesIO(data), chunk_bytes=7, max_offsets=4
        )
        self.assertEqual(consumed, len(data))
        self.assertEqual(digest, hashlib.sha256(data).hexdigest())
        self.assertEqual(matches["libcodecengine"]["count"], 1)
        self.assertEqual(matches["libcodecengine"]["offsets"], [4])
        self.assertEqual(matches["h264"]["count"], 1)

    def test_qnx_and_harman_integration_markers_are_case_insensitive(self):
        data = (
            b"X/pps/services/launcher/control HMI-Notification "
            b"screen_create_window_group PhoneProjectionService ModuleLink "
            b"event-source-handsfree HFP_CALL_INCOMING "
            b"/pps/services/bluetooth/handsfree/status"
        )
        _, matches, _ = _scan_stream(
            io.BytesIO(data), chunk_bytes=11, max_offsets=4
        )
        self.assertEqual(matches["pps_launcher"]["count"], 1)
        self.assertEqual(
            matches["pps_launcher"]["offsets"],
            [data.lower().index(b"/pps/services/launcher")],
        )
        self.assertEqual(matches["hmi_notification"]["count"], 1)
        self.assertEqual(matches["screen_window_group"]["count"], 1)
        self.assertEqual(matches["phone_projection_service"]["count"], 1)
        self.assertEqual(matches["modulelink"]["count"], 1)
        self.assertEqual(matches["hnm_handsfree_plugin"]["count"], 1)
        self.assertEqual(matches["hnm_hfp_call_incoming"]["count"], 1)
        self.assertEqual(matches["pps_bluetooth_handsfree"]["count"], 1)

    def test_offset_cap_preserves_full_count(self):
        data = b"h264--h264--h264"
        _, matches, _ = _scan_stream(io.BytesIO(data), chunk_bytes=5, max_offsets=1)
        self.assertEqual(matches["h264"]["count"], 3)
        self.assertEqual(matches["h264"]["offsets"], [0])
        self.assertTrue(matches["h264"]["offsets_truncated"])

    def test_invalid_scan_limits_fail(self):
        with self.assertRaises(ValueError):
            _scan_stream(io.BytesIO(b"x"), chunk_bytes=0)
        with self.assertRaises(ValueError):
            _scan_stream(io.BytesIO(b"x"), max_offsets=-1)


class RootTests(unittest.TestCase):
    def test_reports_relative_paths_hashes_and_controlled_markers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "hidden_hbc"
            target = root / "usr" / "lib" / "libcodecengine.so.1"
            target.parent.mkdir(parents=True)
            payload = b"prefix decodeCombo middle screen_create_window_buffers suffix"
            target.write_bytes(payload)
            (root / "ordinary.bin").write_bytes(b"private unrelated bytes")

            report = scan_root(root, chunk_bytes=9)
            self.assertEqual(report["root_label"], "hidden_hbc")
            self.assertEqual(report["files_scanned"], 2)
            self.assertEqual(len(report["findings"]), 1)
            finding = report["findings"][0]
            self.assertEqual(finding["path"], "usr/lib/libcodecengine.so.1")
            self.assertEqual(finding["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertIn("libcodecengine", finding["filename_tags"])
            self.assertEqual(
                finding["content_markers"]["decodecombo"]["offsets"],
                [payload.lower().index(b"decodecombo")],
            )
            rendered = json.dumps(report)
            self.assertNotIn("private unrelated bytes", rendered)
            self.assertNotIn(str(root.resolve()), rendered)

    def test_oversized_file_is_explicitly_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            root.mkdir()
            (root / "h264_blob.bin").write_bytes(b"x" * 9)
            report = scan_root(root, max_file_bytes=8)
            self.assertEqual(report["files_scanned"], 0)
            self.assertEqual(report["files_skipped"], 1)
            self.assertEqual(report["skipped"][0]["path"], "h264_blob.bin")
            self.assertEqual(report["findings"], [])

    def test_build_report_totals_multiple_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            roots = [base / "one", base / "two"]
            for root in roots:
                root.mkdir()
            (roots[0] / "sgx530.conf").write_bytes(b"gpu")
            (roots[1] / "boot.sh").write_bytes(b"startup-omap3730")
            report = build_report(roots)
            self.assertEqual(report["format"], "qnx-media-runtime-evidence-v1")
            self.assertEqual(report["totals"]["roots"], 2)
            self.assertEqual(report["totals"]["files_scanned"], 2)
            self.assertEqual(report["totals"]["findings"], 2)


if __name__ == "__main__":
    unittest.main()
