import json
import tempfile
import unittest
from pathlib import Path

from analysis_tools.native_endpoint_census import correlate, scan_native_roots


class NativeEndpointCensusTests(unittest.TestCase):
    def test_candidate_strings_are_bounded_metadata_and_correlate_exactly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = b"\0bind\0listen\0svc.example.input\0/dev/example\0"
            (root / "service.bin").write_bytes(payload)

            result = scan_native_roots(
                {"native": root}, ["svc.example.input", "/dev/example"]
            )

            self.assertEqual(result["coverage"]["files"], 1)
            self.assertEqual(result["coverage"]["matched_files"], 1)
            record = next(
                item for item in result["records"]
                if item["name"] == "svc.example.input"
            )
            self.assertEqual(record["artifact"], "native/service.bin")
            self.assertEqual(record["kind"], "bounded_string_presence")
            self.assertEqual(record["classification"], "PROVED")
            self.assertIsInstance(record["offset"], int)
            self.assertEqual(len(record["sha256"]), 64)
            serialized = json.dumps(result)
            self.assertNotIn(str(root), serialized)
            self.assertNotIn("payload", serialized.lower())

            matches = correlate(
                [{"id": "java-1", "endpoint": "svc.example.input"}],
                result["records"],
            )
            self.assertEqual(matches[0]["match_kind"], "exact_endpoint_name")
            self.assertEqual(matches[0]["classification"], "PROVED")
            self.assertEqual(matches[0]["production_enabled"], "UNKNOWN")
            self.assertEqual(matches[0]["externally_reachable"], "UNKNOWN")

    def test_raw_words_and_archive_data_never_become_structured_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "words.bin").write_bytes(b"bind\0listen\0MsgSend\0")
            (root / "archive.zip").write_bytes(
                b"PK\x03\x04socket\0bind\0svc.example.input\0"
            )

            result = scan_native_roots({"native": root}, ["svc.example.input"])

            self.assertFalse(any(
                record["kind"] in ("structured_import", "native_call_edge")
                for record in result["records"]
            ))
            self.assertTrue(any(
                error["message"] == "archive-like file skipped"
                for error in result["errors"]
            ))

    def test_oversized_files_and_symlinks_are_skipped_explicitly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "large.bin").write_bytes(b"x" * 65)
            (root / "small.bin").write_bytes(b"svc.example.input")
            link = root / "linked.bin"
            try:
                link.symlink_to(root / "small.bin")
            except OSError:
                link = None

            result = scan_native_roots(
                {"native": root}, ["svc.example.input"], max_file_bytes=64
            )

            self.assertEqual(result["coverage"]["oversized_files"], 1)
            self.assertTrue(any(
                error["artifact"] == "native/large.bin"
                and error["message"] == "file size limit exceeded"
                for error in result["errors"]
            ))
            if link is not None:
                self.assertEqual(result["coverage"]["skipped_links"], 1)

    def test_invalid_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "candidate"):
                scan_native_roots({"native": root}, [])
            with self.assertRaisesRegex(ValueError, "size"):
                scan_native_roots({"native": root}, ["endpoint"], max_file_bytes=0)
            with self.assertRaisesRegex(ValueError, "directory"):
                scan_native_roots({"native": root / "missing"}, ["endpoint"])


if __name__ == "__main__":
    unittest.main()
