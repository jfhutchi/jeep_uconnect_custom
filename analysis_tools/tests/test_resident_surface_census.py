import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from analysis_tools.resident_surface_census import (
    ScanLimits,
    census_roots,
    classify_reference,
    parse_properties,
    resolve_focus_dispatch_candidates,
    write_census_outputs,
)
from analysis_tools.java_classfile import ClassModel, MemberEdge, MethodModel
from analysis_tools.tests.test_java_classfile import class_fixture


class ResidentSurfaceCensusTests(unittest.TestCase):
    def test_focus_dispatch_resolves_superclass_virtual_call_as_candidate(self):
        abstract_method = MethodModel(
            "waitForNewCommand", "()Z", 0x0401, (), (), (), (), (),
        )
        concrete_method = MethodModel(
            "waitForNewCommand", "()Z", 0x0001, (), (), (), (), (),
        )
        caller_method = MethodModel(
            "run", "()V", 0x0001, (),
            (
                MemberEdge(
                    7, "invoke_virtual", "example/CommandSource",
                    "waitForNewCommand", "()Z", "invokevirtual", 1,
                ),
            ),
            (), (), (),
        )
        models = {
            "example/CommandSource": ClassModel(
                0, 49, 0x0421, "example/CommandSource", "java/lang/Object",
                (), (), (abstract_method,), (), (), (), (),
            ),
            "example/SocketSource": ClassModel(
                0, 49, 0x0021, "example/SocketSource", "example/CommandSource",
                (), (), (concrete_method,), (), (), (), (),
            ),
            "example/Looper": ClassModel(
                0, 49, 0x0021, "example/Looper", "java/lang/Object",
                ("java/lang/Runnable",), (), (caller_method,), (), (), (), (),
            ),
        }

        candidates = resolve_focus_dispatch_candidates(models, "example/SocketSource")

        self.assertEqual(
            candidates,
            [
                (
                    "example/Looper", "run", "()V", 7,
                    "example/SocketSource", "waitForNewCommand", "()Z",
                    "superclass_virtual_override_candidate",
                )
            ],
        )

    def test_reference_rules_cover_every_requested_surface_family(self):
        cases = [
            ("java/lang/ClassLoader", "loadClass", "dynamic_loading"),
            ("java/lang/reflect/Method", "invoke", "reflection"),
            ("example/WidgetFactory", "create", "factory_provider"),
            ("java/util/jar/JarFile", "getEntry", "resource_package_loading"),
            ("org/mozilla/javascript/Context", "evaluateString", "scripting_interpreter"),
            ("java/net/URL", "openConnection", "url_protocol"),
            ("com/harman/webkit/Browser", "navigate", "browser_webkit"),
            ("javax/xml/parsers/DocumentBuilder", "parse", "structured_data"),
            ("java/net/ServerSocket", "accept", "network_service"),
            ("com/harman/service/SvcIPC", "sendRequest", "ipc_service"),
            ("com/harman/media/Importer", "importFile", "media_import"),
            ("java/io/FileInputStream", "<init>", "user_file_resource"),
            ("example/PluginRegistry", "registerProvider", "plugin_registration"),
        ]
        observed = set()
        for owner, name, category in cases:
            with self.subTest(category=category):
                categories = classify_reference(owner, name, "()V", "example/Caller")
                self.assertIn(category, categories)
                observed.update(categories)
        self.assertTrue(
            {
                "dynamic_loading", "reflection", "factory_provider",
                "resource_package_loading", "scripting_interpreter",
                "url_protocol", "browser_webkit", "structured_data",
                "network_service", "ipc_service", "media_import",
                "user_file_resource", "plugin_registration",
            }.issubset(observed)
        )

    def test_properties_keep_duplicates_and_java_last_value(self):
        result = parse_properties(b"provider=example.One\nprovider: example.Two\nflag=true\n")
        self.assertEqual(result["values"]["provider"], "example.Two")
        self.assertEqual(result["duplicates"], ["provider"])
        self.assertEqual(result["entries"][0], ["provider", "example.One"])

    def test_census_is_deterministic_metadata_only_and_focus_aware(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "resident"
            root.mkdir()
            for name in ("z.jar", "a.jar"):
                with zipfile.ZipFile(root / name, "w") as archive:
                    archive.writestr("example/Server.class", class_fixture())
                    archive.writestr(
                        "xlet.properties",
                        "xlet.class=example.Server\nprovider=example.Provider\n",
                    )
            result = census_roots(
                {"fixture": root}, focus_class="example/Server", broad=True,
                limits=ScanLimits(max_archives=10, max_classes=20),
            )
            self.assertEqual(result["coverage"]["archives"], 2)
            self.assertEqual(result["coverage"]["class_occurrences"], 2)
            self.assertEqual(result["coverage"]["unique_classes"], 1)
            self.assertEqual(len(result["focus"]["occurrences"]), 2)
            self.assertTrue(any(
                item["category"] == "network_service"
                for item in result["surfaces"]
            ))
            network = next(
                item for item in result["surfaces"]
                if item["category"] == "network_service"
            )
            self.assertEqual(network["classification"], "PROVED")
            self.assertEqual(network["origin"]["classification"], "UNKNOWN")
            self.assertIn("external_origin", network["missing_links"])

            first_dir = Path(temporary) / "first"
            second_dir = Path(temporary) / "second"
            write_census_outputs(result, first_dir)
            write_census_outputs(result, second_dir)
            first = {path.name: path.read_bytes() for path in first_dir.iterdir()}
            second = {path.name: path.read_bytes() for path in second_dir.iterdir()}
            self.assertEqual(first, second)
            self.assertEqual(
                set(first),
                {
                    "activation_call_paths.json",
                    "java_extension_surfaces.json",
                    "network_ipc_endpoints.json",
                    "user_controlled_input_surfaces.json",
                },
            )
            for data in first.values():
                self.assertNotIn(str(root).encode("utf-8"), data)
                json.loads(data)

    def test_archive_traversal_and_duplicate_members_are_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with warnings.catch_warnings(), zipfile.ZipFile(root / "bad.jar", "w") as archive:
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr("../escape.class", class_fixture())
                archive.writestr("example/Server.class", class_fixture())
                archive.writestr("example/Server.class", class_fixture())
            result = census_roots(
                {"fixture": root}, focus_class="example/Server", broad=False,
                limits=ScanLimits(max_archives=2, max_classes=10),
            )
            messages = [error["message"] for error in result["errors"]]
            self.assertTrue(any("unsafe archive member" in message for message in messages))
            self.assertTrue(any("duplicate archive member" in message for message in messages))

    def test_limits_and_symlinks_fail_or_skip_explicitly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index in range(2):
                with zipfile.ZipFile(root / f"{index}.jar", "w") as archive:
                    archive.writestr("example/Server.class", class_fixture())
            with self.assertRaisesRegex(ValueError, "archive limit"):
                census_roots(
                    {"fixture": root}, focus_class="example/Server", broad=False,
                    limits=ScanLimits(max_archives=1),
                )

    def test_focus_mode_omits_unrelated_surface_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            unrelated = class_fixture().replace(b"example/Server", b"example/OtherX")
            with zipfile.ZipFile(root / "fixture.jar", "w") as archive:
                archive.writestr("example/Server.class", class_fixture())
                archive.writestr("example/OtherX.class", unrelated)
            result = census_roots(
                {"fixture": root}, focus_class="example/Server", broad=False,
                limits=ScanLimits(max_archives=2, max_classes=10),
            )
            self.assertTrue(result["surfaces"])
            self.assertEqual(
                {surface["component"] for surface in result["surfaces"]},
                {"example/Server"},
            )


if __name__ == "__main__":
    unittest.main()
