import hashlib
import io
import unittest

from analysis_tools.synctool_log_probe import runtime_value_token, scan_markers


class LogProbeTests(unittest.TestCase):
    def test_distinguishes_binary_format_strings_from_runtime_candidates(self) -> None:
        data = b"App SKU ID %d\0App SKU ID 123\nDevice.nng read, valid:1 t:example"
        hits = list(scan_markers(io.BytesIO(data), chunk_size=8))
        self.assertEqual([hit.offset for hit in hits], [0, 14, 29])
        self.assertEqual([hit.kind for hit in hits],
                         ["format_string", "runtime_candidate", "runtime_candidate"])
        self.assertEqual(hits[1].app_sku, 123)

    def test_chunk_boundaries_do_not_drop_or_duplicate_markers(self) -> None:
        data = b"x" * 17 + b"Found activable license record <%s>" + b"y" * 40
        for size in (1, 7, 32, 64, 1024):
            with self.subTest(chunk_size=size):
                hits = list(scan_markers(io.BytesIO(data), chunk_size=size))
                self.assertEqual(len(hits), 1)
                self.assertEqual(hits[0].offset, 17)
                self.assertEqual(hits[0].kind, "format_string")

    def test_truncated_marker_suffix_is_explicitly_unclassified(self) -> None:
        hits = list(scan_markers(io.BytesIO(b"App SKU ID "), chunk_size=2))
        self.assertEqual(hits[0].kind, "unclassified")

    def test_signed_decimal_app_sku_matches_percent_d_logging(self) -> None:
        hit = list(scan_markers(io.BytesIO(b"App SKU ID -1\n"), chunk_size=3))[0]
        self.assertEqual(hit.kind, "runtime_candidate")
        self.assertEqual(hit.app_sku, -1)

    def test_does_not_emit_record_names_or_arbitrary_log_contents(self) -> None:
        hit = list(scan_markers(io.BytesIO(
            b"Found invalid license record <private-name> type:123")))[0]
        self.assertEqual(hit.kind, "runtime_candidate")
        self.assertNotIn("private-name", str(hit))

    def test_finds_copy_plan_exclusion_without_disclosing_filename(self) -> None:
        hit = list(scan_markers(io.BytesIO(
            b"Removing file from file copy: <private-name>")))[0]
        self.assertEqual(hit.marker, "excluded_file")
        self.assertEqual(hit.kind, "runtime_candidate")
        self.assertNotIn("private-name", str(hit))

    def test_runtime_value_token_correlates_without_disclosing_value(self) -> None:
        private_value = b"same-private-runtime-value"
        data = (
            b"Found incompatible activable license record <" + private_value + b">\n"
            b"Removing file from file copy: <" + private_value + b">"
        )
        hits = list(scan_markers(io.BytesIO(data), chunk_size=9))
        expected = hashlib.sha256(private_value).hexdigest()[:16]
        self.assertEqual([hit.value_token for hit in hits], [expected, expected])
        self.assertNotIn(private_value.decode(), repr(hits))
        self.assertEqual(runtime_value_token(private_value + b">"), expected)

    def test_incomplete_or_oversized_runtime_value_is_not_tokenized(self) -> None:
        self.assertIsNone(runtime_value_token(b"incomplete"))
        self.assertIsNone(runtime_value_token(b"x" * 513 + b">"))
        self.assertIsNone(runtime_value_token(b"not\x00printable>"))

    def test_rejects_invalid_chunk_size(self) -> None:
        with self.assertRaises(ValueError):
            list(scan_markers(io.BytesIO(), chunk_size=0))


if __name__ == "__main__":
    unittest.main()
