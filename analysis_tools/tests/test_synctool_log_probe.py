import hashlib
import io
import unittest

from analysis_tools.synctool_log_probe import (
    TARGET_LICENSE_FILENAME,
    angle_value_tokens,
    runtime_line_token,
    runtime_value_token,
    scan_markers,
)


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
        expected = hashlib.sha256(private_value).hexdigest()
        self.assertEqual([hit.value_token for hit in hits], [expected, expected])
        self.assertNotIn(private_value.decode(), repr(hits))
        self.assertEqual(runtime_value_token(private_value + b">"), expected)

    def test_known_my14_filename_is_flagged_without_printing_it(self) -> None:
        data = b"Removing file from file copy: <" + TARGET_LICENSE_FILENAME + b">"
        hit = list(scan_markers(io.BytesIO(data), chunk_size=11))[0]
        self.assertTrue(hit.target_match)
        self.assertNotIn(TARGET_LICENSE_FILENAME.decode(), repr(hit))

    def test_incomplete_or_oversized_runtime_value_is_not_tokenized(self) -> None:
        self.assertIsNone(runtime_value_token(b"incomplete"))
        self.assertIsNone(runtime_value_token(b"x" * 513 + b">"))
        self.assertIsNone(runtime_value_token(b"not\x00printable>"))

    def test_rejects_invalid_chunk_size(self) -> None:
        with self.assertRaises(ValueError):
            list(scan_markers(io.BytesIO(), chunk_size=0))


    def test_identity_planes_are_tokenized_without_disclosure(self) -> None:
        swid = b"private-device-swid"
        platform = b"private-platform-id"
        data = (
            b"DeviceCode: private-device-code\n"
            b"ContentCode: private-content-code\n"
            b"Platform ID: " + platform + b"\n"
            b"SWID: " + swid + b"\n"
            b"Using IDs\n<" + swid + b"> <" + platform + b">\n"
        )
        hits = list(scan_markers(io.BytesIO(data), chunk_size=7))
        by_marker = {hit.marker: hit for hit in hits}
        self.assertEqual(
            by_marker["swid"].identity_tokens,
            (hashlib.sha256(swid).hexdigest(),),
        )
        self.assertEqual(
            by_marker["using_ids"].identity_tokens,
            (hashlib.sha256(swid).hexdigest(),
             hashlib.sha256(platform).hexdigest()),
        )
        self.assertNotIn(swid.decode(), repr(hits))
        self.assertNotIn(platform.decode(), repr(hits))

    def test_application_record_count_uses_preceding_return_value(self) -> None:
        data = (
            b"Returning 2\n"
            b"# of license record for license type Application\n"
        )
        hit = list(scan_markers(io.BytesIO(data), chunk_size=5))[0]
        self.assertEqual(hit.marker, "application_license_records")
        self.assertEqual(hit.kind, "runtime_candidate")
        self.assertEqual(hit.record_count, 2)

    def test_identity_format_strings_are_not_runtime_values(self) -> None:
        data = b"Platform ID: %s\0Using IDs <%s> <%s>"
        hits = list(scan_markers(io.BytesIO(data), chunk_size=4))
        self.assertEqual([hit.kind for hit in hits],
                         ["format_string", "format_string"])
        self.assertEqual([hit.identity_tokens for hit in hits], [(), ()])

    def test_identity_token_helpers_reject_incomplete_or_format_values(self) -> None:
        value = b"private-value"
        expected = hashlib.sha256(value).hexdigest()
        self.assertEqual(runtime_line_token(b"  " + value + b"\n"), expected)
        self.assertEqual(
            angle_value_tokens(b" <" + value + b"> <" + value + b">"),
            (expected, expected),
        )
        self.assertIsNone(runtime_line_token(b"%s\n"))
        self.assertEqual(angle_value_tokens(b"<%s> <private>"), ())


if __name__ == "__main__":
    unittest.main()
