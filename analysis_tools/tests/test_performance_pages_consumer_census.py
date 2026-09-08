import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import warnings
from zipfile import ZipFile

from analysis_tools import performance_pages_consumer_census as census
from analysis_tools.tests.test_java_classfile import Pool, member, u2


def reader_fixture():
    pool = Pool()
    this_class = pool.class_("example/TimerReader")
    super_class = pool.class_("java/lang/Object")
    file_init = pool.methodref("java/io/FileInputStream", "<init>", "(Ljava/lang/String;)V")
    literal_utf = pool.utf("file:///tmp/report.html")
    literal = pool.add(b"\x08" + u2(literal_utf))
    code = b"\x12" + bytes([literal]) + b"\x57\x01\xb7" + u2(file_init) + b"\xb1"
    method = member(pool, "read", "()V", code)
    return (
        bytes.fromhex("cafebabe00000031") + pool.build()
        + struct.pack(">HHHH", 0x0021, this_class, super_class, 0)
        + u2(0) + u2(1) + method + u2(0)
    )


class ConsumerCensusTests(unittest.TestCase):
    def test_substring_evidence_hides_unreviewed_literal(self):
        row = census.literal_evidence("private-prefix/file:///tmp/report.html?token=hidden")
        self.assertEqual(row["matched_terms"], [".html", "file://"])
        self.assertNotIn("reviewed_exact_value", row)
        self.assertNotIn("hidden", repr(row))

    def test_candidate_api_categories_cover_reader_and_viewer(self):
        categories = census.classify_edge("java/io/FileInputStream", "<init>", "(Ljava/lang/String;)V")
        self.assertIn("file_open_read_enumerate", categories)
        categories = census.classify_edge("example/WebView", "openHtml", "(Ljava/lang/String;)V")
        self.assertIn("chooser_browser_webview_html_mime", categories)

    def test_fixture_detects_embedded_html_reader_without_promoting_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jar = root / "secondary_iso/usr/share/XLETS/kim_packages/KIM19/fixture.jar"
            jar.parent.mkdir(parents=True)
            with ZipFile(jar, "w") as archive:
                archive.writestr("example/TimerReader.class", reader_fixture())
            report = census.scan_sources(root, [jar], kim_count=1, common_count=0)
            self.assertEqual(report["coverage"]["class_entries"], 1)
            self.assertEqual(report["scoped_consumer_result"]["non_performance_kim_html_or_file_uri_literal_count"], 1)
            self.assertIn("syntactic candidates matched", report["scoped_consumer_result"]["conclusion"])
            self.assertTrue(report["scoped_consumer_result"]["runtime_reachability"].startswith("UNKNOWN"))
            self.assertTrue(any("file_open_read_enumerate" in row["categories"] for row in report["candidate_api_invocations"]))

    def test_malformed_class_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jar = root / "bad.jar"
            with ZipFile(jar, "w") as archive:
                archive.writestr("Bad.class", b"not a class")
            with self.assertRaisesRegex(ValueError, "class parse failure"):
                census.scan_sources(root, [jar], kim_count=0, common_count=0)

    def test_duplicate_member_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jar = root / "duplicate.jar"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with ZipFile(jar, "w") as archive:
                    archive.writestr("example/TimerReader.class", reader_fixture())
                    archive.writestr("example/TimerReader.class", reader_fixture())
            with self.assertRaisesRegex(ValueError, "duplicate archive member"):
                census.scan_sources(root, [jar], kim_count=0, common_count=0)

    def test_canonical_write_and_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            report = {"z": 1, "a": "non-ascii: \u00e9"}
            self.assertEqual(census.write_or_check(path, report, False), 0)
            self.assertEqual(path.read_bytes(), b'{\n  "a": "non-ascii: \\u00e9",\n  "z": 1\n}\n')
            self.assertEqual(census.write_or_check(path, {"a": report["a"], "z": 1}, True), 0)
            path.write_bytes(b"stale")
            self.assertEqual(census.write_or_check(path, report, True), 1)
            self.assertEqual(path.read_bytes(), b"stale")

    def test_output_under_corpus_rejected_before_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            with mock.patch.object(census, "build_report") as build:
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        census.main(["--corpus", directory, "--output", str(output)])
                build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
