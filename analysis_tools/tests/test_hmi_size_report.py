import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from analysis_tools.hmi_size_report import inventory, budget


class SizeReportTests(unittest.TestCase):
    def test_logical_and_assumed_allocation_are_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'one.txt').write_bytes(b'x' * 4097)
            (root / 'empty.txt').write_bytes(b'')
            report = inventory(root, 4096)
            self.assertEqual(report['logical_bytes'], 4097)
            self.assertEqual(report['estimated_allocated_bytes'], 8192)
            self.assertEqual(report['file_count'], 2)

    def test_caps_and_reserve_are_both_enforced(self):
        self.assertTrue(budget(15_000_000, 4_000_000, 8_000_000)['within_envelope'])
        self.assertFalse(budget(15_000_001, 0, 0)['within_envelope'])
        self.assertFalse(budget(1, 4_000_001, 0)['within_envelope'])
        self.assertFalse(budget(1, 0, 8_000_001)['within_envelope'])
        self.assertEqual(budget(15_000_000, 4_000_000, 8_000_000)['remaining_bytes'], 50_000_000)

    def test_missing_root_and_invalid_numbers_are_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                inventory(Path(folder) / 'absent', 4096)
            with self.assertRaises(ValueError):
                inventory(Path(folder), 0)
        with self.assertRaises(ValueError):
            budget(-1, 0, 0)

    def test_empty_target_is_not_a_built_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, '-m', 'analysis_tools.hmi_size_report',
                                     folder, '--kind', 'target-package', '--writable-bytes',
                                     '0', '--temporary-bytes', '0'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('empty', result.stderr)

    def test_target_requires_explicit_peak_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, '-m', 'analysis_tools.hmi_size_report',
                                     folder, '--kind', 'target-package'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('explicit', result.stderr)


if __name__ == '__main__':
    unittest.main()
