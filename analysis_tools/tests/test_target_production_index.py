import hashlib
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from analysis_tools.resident_surface_census import ScanLimits
from analysis_tools.target_production_index import (
    api_categories, build_inventory, normalize_part, resolve_part,
)
from analysis_tools.tests.test_java_classfile import class_fixture


class TargetProductionIndexTests(unittest.TestCase):
    def test_exact_suffix_order_and_read_window(self):
        self.assertEqual(normalize_part("68224525AM"), "68224525")
        self.assertEqual(normalize_part("68224525amMORE"), "68224525")
        self.assertEqual(normalize_part("123456789A"), "123456789")
        self.assertEqual(normalize_part("68224525"), "68224525")
        self.assertEqual(normalize_part(" 68224525AM"), " 68224525A")
        self.assertEqual(normalize_part("bad"), "bad")
        self.assertEqual(normalize_part(""), "")
        self.assertIsNone(normalize_part(None))
        self.assertEqual(normalize_part(None, open_succeeded=False), "PN ERROR")

    def test_exact_key_last_assignment_fallback_and_block_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.lua"
            path.write_text('kim_pkg_map = {}\nkim_pkg_map["68224525"] = "KIM1"\n'
                            '--[[\nkim_pkg_map["68224525"] = "KIM3"\n]]\n'
                            'kim_pkg_map["68224525"] = "KIM19" -- MY14 VP4 NA\n')
            result = resolve_part(path, "68224525AM")
            self.assertEqual(result["selected_package"], "KIM19")
            self.assertEqual([m["line"] for m in result["matching_assignments"]], [2, 6])
            self.assertFalse(result["fallback_used"])
            self.assertEqual(resolve_part(path, "68224526AM")["selected_package"], "KIM0")
            self.assertTrue(resolve_part(path, None)["fallback_used"])
            path.write_text('kim_pkg_map = {}\nos.execute("not allowed")\n')
            with self.assertRaises(ValueError):
                resolve_part(path, "68224525AM")

    def test_inventory_preserves_member_identity_and_call_descriptor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prog = root / "xlets/id/prog"
            (prog / "jars").mkdir(parents=True)
            (prog / "xlet.properties").write_text(
                'xlet.name=Demo\nxlet.version=1\nxlet.appId=id\n'
                'xlet.mainClass=example.Server\nxlet.jarFile=app.jar\n')
            with zipfile.ZipFile(prog / "jars/app.jar", "w") as jar:
                jar.writestr("example/Server.class", class_fixture())
                jar.writestr("security.policy", 'grant { permission java.io.FilePermission "/data", "read"; };')
                jar.writestr("META-INF/services/example.Service", "private fixture payload")
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            result = build_inventory(root)
            self.assertEqual(result, build_inventory(root))
            self.assertEqual(result["coverage"]["classes"], 1)
            app = result["applications"][0]
            self.assertEqual(app["registered_on_target"], "UNKNOWN")
            sites = result["jars"][0]["api_sites"]
            socket = next(s for s in sites if s["owner"] == "java/net/ServerSocket")
            self.assertIn("caller_descriptor", socket)
            self.assertIn("descriptor", socket)
            self.assertNotIn("private fixture payload", str(result))
            self.assertTrue(result["jars"][0]["declared_permissions"])
            self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_invalid_or_oversized_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(root / "bad.jar", "w") as jar:
                jar.writestr("Bad.class", b"bad class")
            with self.assertRaises(ValueError):
                build_inventory(root)
            with self.assertRaisesRegex(ValueError, "size limit"):
                build_inventory(root, ScanLimits(max_archive_bytes=1))

    def test_missing_declared_jar_is_not_reported_as_inventory_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "xlet.properties").write_text('xlet.jarFile=missing.jar\nxlet.mainClass=Missing\n')
            with self.assertRaisesRegex(ValueError, "missing declared"):
                build_inventory(root)

    def test_duplicate_members_and_missing_main_are_explicit_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jars").mkdir()
            jarpath = root / "jars/app.jar"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(jarpath, "w") as jar:
                    jar.writestr("same.txt", "one")
                    jar.writestr("same.txt", "two")
            with self.assertRaisesRegex(ValueError, "duplicate archive member"):
                build_inventory(root)
            with zipfile.ZipFile(jarpath, "w") as jar:
                jar.writestr("example/Server.class", class_fixture())
            (root / "xlet.properties").write_text('xlet.jarFile=app.jar\nxlet.mainClass=Missing\n')
            with self.assertRaisesRegex(ValueError, "missing declared main"):
                build_inventory(root)

    def test_api_names_are_candidates_not_claims_of_external_control(self):
        self.assertIn("mqtt", api_categories("org/eclipse/paho/client/mqttv3/MqttClient", "connect"))
        self.assertIn("appmanager_svcipc", api_categories("com/harman/svcipc/SvcIpcClient", "invoke"))
        self.assertIn("class_loading", api_categories("java/lang/ClassLoader", "getResourceAsStream"))
        self.assertNotIn("process_launch", api_categories("example/Executor", "exec"))


if __name__ == "__main__":
    unittest.main()
