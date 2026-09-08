import hashlib
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

from analysis_tools.stock_capability_index import build_index, categories, package_selection
from analysis_tools.tests.test_java_classfile import class_fixture


class StockCapabilityIndexTests(unittest.TestCase):
    def test_duplicate_occurrences_preserve_identity_without_running_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = class_fixture()
            for name in ("a.jar", "b.jar"):
                with zipfile.ZipFile(root / name, "w") as jar:
                    jar.writestr("example/Server.class", data)
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            first = build_index(root, re.compile("example/Server"))
            self.assertEqual(first, build_index(root, re.compile("example/Server")))
            self.assertEqual(first["coverage"]["class_occurrences"], 2)
            self.assertEqual(first["coverage"]["unique_class_hashes"], 1)
            self.assertEqual(len(first["selected_classes"][0]["occurrences"]), 2)
            self.assertTrue(any(s["owner"] == "java/net/ServerSocket" for s in first["capability_sites"]))
            self.assertTrue(any(s["opcode"] == "putfield" for s in first["incoming_selected"]))
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            self.assertEqual(before, after)

    def test_malformed_class_fails_instead_of_reporting_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(root / "bad.jar", "w") as jar:
                jar.writestr("Broken.class", b"not a class")
            with self.assertRaises(ValueError):
                build_index(root, re.compile(".*"))

    def test_server_factory_and_launch_apis_are_not_missed(self):
        self.assertIn("socket", categories("javax/net/ServerSocketFactory", "createServerSocket"))
        self.assertIn("process_launch", categories("java/lang/Runtime", "exec"))
        self.assertIn("native_library", categories("java/lang/System", "load"))
        self.assertNotIn("process_launch", categories("example/Executor", "exec"))

    def test_package_map_preserves_last_assignment_and_rejects_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.lua"
            path.write_text('kim_pkg_map = {}\nkim_pkg_map["123"] = "KIM1"\n'
                            'kim_pkg_map["123"] = "KIM18" -- replacement\n')
            result = package_selection(path)
            self.assertEqual(result["assignment_count"], 2)
            self.assertEqual(result["effective_package_counts"], {"KIM18": 1})
            path.write_text('os.execute("never execute input")\n')
            with self.assertRaises(ValueError):
                package_selection(path)


if __name__ == "__main__":
    unittest.main()
