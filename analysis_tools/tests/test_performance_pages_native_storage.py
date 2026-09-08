import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from analysis_tools import performance_pages_native_storage as native


class NativeStorageTests(unittest.TestCase):
    def test_unreviewed_source_rejected_before_parsing(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            native.require_source(b'unreviewed native artifact')

    def test_canonical_bytes_and_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            report = {'z': 1, 'a': 'non-ascii: \u00e9'}
            self.assertEqual(native.write_or_check(path, report, False), 0)
            expected = b'{\n  "a": "non-ascii: \\u00e9",\n  "z": 1\n}\n'
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(native.write_or_check(path, {'a': report['a'], 'z': 1}, True), 0)
            path.write_bytes(expected.replace(b'\n', b'\r\n'))
            stale = path.read_bytes()
            self.assertEqual(native.write_or_check(path, report, True), 1)
            self.assertEqual(path.read_bytes(), stale)

    def test_check_missing_does_not_create_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'missing' / 'report.json'
            self.assertEqual(native.write_or_check(path, {}, True), 1)
            self.assertFalse(path.parent.exists())

    def test_output_under_corpus_rejected_before_source_read(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(native, 'build_report') as build:
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        native.main(['--corpus', directory, '--output', str(Path(directory) / 'report.json')])
                build.assert_not_called()

    def test_selected_windows_fit_reviewed_functions(self):
        names = set()
        for name, start, end in native.WINDOWS:
            self.assertNotIn(name, names)
            names.add(name)
            self.assertEqual(start % 4, 0)
            self.assertEqual(end % 4, 0)
            self.assertLess(start, end)
            self.assertTrue(any(base <= start < end <= base + size for _, base, size in native.FUNCTIONS))


if __name__ == '__main__':
    unittest.main()
