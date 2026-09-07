import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

from analysis_tools.resident_package_inspect import (
    PackageInspectionError,
    inspect_path,
    render_json,
)


APP_ID = "11111111-2222-4333-8444-555555555555"
MAIN_CLASS = "example.hello.HelloXlet"


def _digest(data):
    return base64.b64encode(hashlib.sha1(data).digest()).decode("ascii")


def _manifest(payload_members, signed_descriptor):
    lines = ["Manifest-Version: 1.0", "Created-By: synthetic-test", ""]
    members = dict(payload_members)
    members["xlet.properties"] = signed_descriptor
    for name in sorted(members):
        lines.extend(
            [
                "Name: %s" % name,
                "SHA1-Digest: %s" % _digest(members[name]),
                "",
            ]
        )
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def _signature_file(manifest):
    return (
        "Signature-Version: 1.0\r\n"
        "SHA1-Digest-Manifest: %s\r\n\r\n" % _digest(manifest)
    ).encode("ascii")


class ResidentPackageInspectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.case_number = 0

    def tearDown(self):
        self.temporary.cleanup()

    def _inspect(self, path, **kwargs):
        with mock.patch(
            "analysis_tools.resident_package_inspect._certificate_metadata",
            return_value=([{"certificate_sha256": "synthetic-test"}], []),
        ):
            return inspect_path(path, **kwargs)

    def _properties(self, **overrides):
        values = {
            "xlet.appId": APP_ID,
            "xlet.jarFile": "%s.jar" % APP_ID,
            "xlet.mainClass": MAIN_CLASS,
            "xlet.name": "Synthetic Hello",
            "xlet.vendor": "Synthetic Test",
            "xlet.version": "0.1.0",
            "xlet.policy": "security.policy",
            "xlet.policy.default": "full.policy",
            "xlet.daemon": "false",
            "xlet.isAudio": "false",
            "xlet.PauseAllowed": "false",
        }
        values.update(overrides)
        return ("\n".join("%s=%s" % item for item in sorted(values.items())) + "\n").encode(
            "ascii"
        )

    def _write_layout(
        self,
        installed_overrides=None,
        signed_overrides=None,
        payload_members=None,
        include_key=True,
        include_signature=True,
        include_magic=True,
        manifest_mutator=None,
    ):
        self.case_number += 1
        app_root = self.root / ("case-%02d" % self.case_number) / APP_ID
        jars = app_root / "prog" / "jars"
        jars.mkdir(parents=True)
        installed = self._properties(**(installed_overrides or {}))
        signed = self._properties(**(signed_overrides or {}))
        (app_root / "prog" / "xlet.properties").write_bytes(installed)
        members = payload_members or {
            "example/hello/HelloXlet.class": b"class-48",
            "xlet.properties": signed,
        }
        with zipfile.ZipFile(jars / (APP_ID + ".jar"), "w") as archive:
            for name, data in sorted(members.items()):
                archive.writestr(name, data)
        if include_magic:
            (jars / "magic.txt").write_bytes(b"HB_CMC")
        if include_key:
            manifest = _manifest(members, signed)
            if manifest_mutator:
                manifest = manifest_mutator(manifest)
            with zipfile.ZipFile(jars / "key.jar", "w") as archive:
                archive.writestr("META-INF/MANIFEST.MF", manifest)
                archive.writestr("xlet.properties", signed)
                if include_signature:
                    archive.writestr("META-INF/SYNTH.SF", _signature_file(manifest))
                    archive.writestr("META-INF/SYNTH.RSA", b"synthetic-not-a-certificate")
        return app_root

    def test_recognizes_proved_factory_installed_layout(self):
        report = self._inspect(self._write_layout(), hello_profile=True)

        self.assertEqual(report["classification"], "factory-installed-layout-analogue")
        self.assertTrue(report["structure"]["valid"])
        self.assertTrue(report["structure"]["structurally_analogous_to_stock"])
        self.assertEqual(report["application"]["app_id"], APP_ID)
        self.assertEqual(report["application"]["main_class"], MAIN_CLASS)
        self.assertEqual(report["payload"]["member_count"], 2)
        self.assertEqual(report["authentication"]["payload_members_covered"], 2)
        self.assertEqual(report["authentication"]["digest_mismatches"], 0)
        self.assertEqual(report["authentication"]["signature_files"], ["META-INF/SYNTH.SF"])
        self.assertEqual(report["authentication"]["signature_blocks"], ["META-INF/SYNTH.RSA"])
        self.assertTrue(report["authentication"]["manifest_digest_matches"])
        self.assertTrue(report["hello_profile"]["safe"])
        self.assertFalse(report["installability"]["installable"])
        self.assertIn("accepted incoming single-JAR schema", report["installability"]["missing_requirements"])

    def test_installed_and_signed_descriptors_may_rename_payload_only(self):
        report = self._inspect(
            self._write_layout(signed_overrides={"xlet.jarFile": "HelloBuild.jar"})
        )
        self.assertTrue(report["identity"]["signed_installed_core_match"])
        self.assertEqual(
            report["identity"]["allowed_descriptor_differences"],
            ["xlet.jarFile"],
        )

    def test_key_member_digest_name_also_covers_same_named_payload_member(self):
        report = self._inspect(
            self._write_layout(
                payload_members={
                    "example/hello/HelloXlet.class": b"class-48",
                    "xlet.properties": self._properties(),
                }
            )
        )
        self.assertTrue(report["structure"]["valid"])
        self.assertEqual(report["authentication"]["payload_members_covered"], 2)
        self.assertEqual(report["authentication"]["uncovered_payload_members"], [])

    def test_reports_missing_key_as_unsigned_non_installable_skeleton(self):
        report = inspect_path(self._write_layout(include_key=False), hello_profile=True)

        self.assertEqual(report["classification"], "incomplete-installed-layout-skeleton")
        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["structure"]["structurally_analogous_to_stock"])
        self.assertIn("fixed sibling prog/jars/key.jar", report["structure"]["errors"])
        self.assertIn("legitimate detached key.jar envelope", report["installability"]["missing_requirements"])
        self.assertFalse(report["installability"]["installable"])

    def test_rejects_missing_executable_root_descriptor(self):
        report = inspect_path(
            self._write_layout(
                payload_members={"example/hello/HelloXlet.class": b"class-48"}
            )
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertIn("executable JAR root xlet.properties", report["structure"]["errors"])

    def test_rejects_missing_installed_layout_magic(self):
        report = inspect_path(self._write_layout(include_magic=False))

        self.assertFalse(report["structure"]["valid"])
        self.assertIn("prog/jars/magic.txt HB_CMC marker", report["structure"]["errors"])

    def test_rejects_payload_and_key_copy_name_collision_with_different_bytes(self):
        signed = self._properties()
        report = inspect_path(
            self._write_layout(
                payload_members={
                    "example/hello/HelloXlet.class": b"class-48",
                    "xlet.properties": signed + b"# payload-only mutation\n",
                }
            )
        )

        self.assertFalse(report["structure"]["valid"])
        self.assertIn(
            "detached manifest same-name member mismatch",
            report["structure"]["errors"],
        )

    def test_rejects_app_id_directory_mismatch(self):
        app_root = self._write_layout(installed_overrides={"xlet.appId": "different"})
        report = inspect_path(app_root)
        self.assertFalse(report["structure"]["valid"])
        self.assertIn("directory name does not match xlet.appId", report["structure"]["errors"])

    def test_rejects_descriptor_selected_payload_path_escape(self):
        app_root = self._write_layout(
            installed_overrides={"xlet.jarFile": "../../../outside.jar"}
        )
        payload = app_root / "prog" / "jars" / (APP_ID + ".jar")
        (app_root.parent / "outside.jar").write_bytes(payload.read_bytes())

        report = self._inspect(app_root)

        self.assertFalse(report["structure"]["valid"])
        self.assertIn("unsafe installed xlet.jarFile", report["structure"]["errors"])

    def test_rejects_core_identity_mismatch(self):
        report = inspect_path(
            self._write_layout(signed_overrides={"xlet.mainClass": "evil.Other"})
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["identity"]["signed_installed_core_match"])
        self.assertIn("signed and installed xlet.mainClass differ", report["structure"]["errors"])

    def test_rejects_signed_and_installed_token_mismatch(self):
        report = inspect_path(
            self._write_layout(signed_overrides={"xlet.developerToken": "opaque"})
        )

        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["identity"]["signed_installed_protected_match"])
        self.assertIn(
            "signed and installed xlet.developerToken differ",
            report["structure"]["errors"],
        )

    def test_rejects_signed_only_unsafe_lifecycle_field(self):
        report = self._inspect(
            self._write_layout(signed_overrides={"xlet.autostart": "true"}),
            hello_profile=True,
        )

        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["hello_profile"]["safe"])
        self.assertIn("xlet.autostart=true", report["hello_profile"]["prohibited_declarations"])
        self.assertIn(
            "signed and installed xlet.autostart differ",
            report["structure"]["errors"],
        )

    def test_rejects_incomplete_or_incorrect_detached_digest_coverage(self):
        report = inspect_path(
            self._write_layout(
                manifest_mutator=lambda value: value.replace(
                    b"SHA1-Digest: ", b"SHA1-Digest: AAAA", 1
                )
            )
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertGreater(report["authentication"]["digest_mismatches"], 0)

        report = inspect_path(
            self._write_layout(
                payload_members={
                    "example/hello/HelloXlet.class": b"class-48",
                    "resource.txt": b"resource",
                },
                manifest_mutator=lambda value: value.replace(
                    b"Name: resource.txt\r\nSHA1-Digest: "
                    + _digest(b"resource").encode("ascii")
                    + b"\r\n\r\n",
                    b"",
                ),
            )
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertEqual(report["authentication"]["uncovered_payload_members"], ["resource.txt"])

    def test_rejects_unsigned_embedded_descriptor(self):
        descriptor_section = (
            b"Name: xlet.properties\r\nSHA1-Digest: "
            + _digest(self._properties()).encode("ascii")
            + b"\r\n\r\n"
        )
        report = inspect_path(
            self._write_layout(
                manifest_mutator=lambda value: value.replace(descriptor_section, b"")
            )
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["authentication"]["signed_descriptor_covered"])
        self.assertIn("signed xlet.properties manifest coverage", report["structure"]["errors"])

    def test_rejects_missing_signature_pair_and_bad_sf_manifest_digest(self):
        report = inspect_path(self._write_layout(include_signature=False))
        self.assertFalse(report["structure"]["valid"])
        self.assertIn("key.jar JAR-signature metadata", report["structure"]["errors"])

        app_root = self._write_layout()
        key_path = app_root / "prog" / "jars" / "key.jar"
        with zipfile.ZipFile(key_path, "r") as source:
            entries = {name: source.read(name) for name in source.namelist()}
        entries["META-INF/SYNTH.SF"] = entries["META-INF/SYNTH.SF"].replace(
            b"SHA1-Digest-Manifest: ", b"SHA1-Digest-Manifest: AAAA"
        )
        with zipfile.ZipFile(key_path, "w") as output:
            for name, data in sorted(entries.items()):
                output.writestr(name, data)
        report = inspect_path(app_root)
        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["authentication"]["manifest_digest_matches"])

    def test_rejects_decoupled_signature_pair_and_manifest_digest(self):
        app_root = self._write_layout()
        key_path = app_root / "prog" / "jars" / "key.jar"
        with zipfile.ZipFile(key_path, "r") as source:
            entries = {name: source.read(name) for name in source.namelist()}
        manifest = entries["META-INF/MANIFEST.MF"]
        entries["META-INF/SYNTH.SF"] = b"Signature-Version: 1.0\r\n\r\n"
        entries["META-INF/OTHER.SF"] = _signature_file(manifest)
        with zipfile.ZipFile(key_path, "w") as output:
            for name, data in sorted(entries.items()):
                output.writestr(name, data)

        report = self._inspect(app_root)

        self.assertFalse(report["structure"]["valid"])
        self.assertFalse(report["authentication"]["manifest_digest_matches"])
        self.assertIn("key.jar JAR-signature metadata", report["structure"]["errors"])

    def test_rejects_malformed_pkcs7_signature_block(self):
        report = inspect_path(self._write_layout())

        self.assertFalse(report["structure"]["valid"])
        self.assertTrue(report["authentication"]["certificate_parse_errors"])
        self.assertIn("key.jar PKCS#7 certificate metadata", report["structure"]["errors"])

    def test_fails_closed_when_pkcs7_parser_is_unavailable(self):
        with mock.patch(
            "analysis_tools.resident_package_inspect._certificate_metadata",
            return_value=([], ["cryptography dependency unavailable"]),
        ):
            report = inspect_path(self._write_layout())

        self.assertFalse(report["structure"]["valid"])
        self.assertIn("key.jar PKCS#7 certificate metadata", report["structure"]["errors"])

    def test_rejects_missing_manifest_and_signature_versions(self):
        report = self._inspect(
            self._write_layout(
                manifest_mutator=lambda value: value.replace(
                    b"Manifest-Version: 1.0\r\n", b"", 1
                )
            )
        )
        self.assertFalse(report["structure"]["valid"])
        self.assertIn("key.jar manifest version", report["structure"]["errors"])

        app_root = self._write_layout()
        key_path = app_root / "prog" / "jars" / "key.jar"
        with zipfile.ZipFile(key_path, "r") as source:
            entries = {name: source.read(name) for name in source.namelist()}
        entries["META-INF/SYNTH.SF"] = entries["META-INF/SYNTH.SF"].replace(
            b"Signature-Version: 1.0\r\n", b"", 1
        )
        with zipfile.ZipFile(key_path, "w") as output:
            for name, data in sorted(entries.items()):
                output.writestr(name, data)
        report = self._inspect(app_root)
        self.assertFalse(report["structure"]["valid"])
        self.assertIn("key.jar .SF signature version", report["structure"]["errors"])

    def test_hello_profile_reports_privilege_and_lifecycle_declarations(self):
        report = self._inspect(
            self._write_layout(
                installed_overrides={
                    "xlet.autostart": "true",
                    "xlet.daemon": "true",
                    "xlet.isAudio": "true",
                    "xlet.writeEnabled": "true",
                    "xlet.developerToken": "opaque",
                },
                signed_overrides={
                    "xlet.autostart": "true",
                    "xlet.daemon": "true",
                    "xlet.isAudio": "true",
                    "xlet.writeEnabled": "true",
                    "xlet.developerToken": "opaque",
                },
            ),
            hello_profile=True,
        )
        self.assertFalse(report["hello_profile"]["safe"])
        self.assertEqual(
            report["hello_profile"]["prohibited_declarations"],
            [
                "xlet.autostart=true",
                "xlet.daemon=true",
                "xlet.developerToken=<present>",
                "xlet.isAudio=true",
                "xlet.writeEnabled=true",
            ],
        )

    def test_single_jar_candidate_does_not_claim_incoming_schema(self):
        candidate = self.root / "candidate.jar"
        with zipfile.ZipFile(candidate, "w") as archive:
            archive.writestr("xlet.properties", self._properties())
            archive.writestr("example/hello/HelloXlet.class", b"class-48")
        report = inspect_path(candidate)

        self.assertEqual(report["classification"], "single-jar-candidate")
        self.assertEqual(report["container"]["magic_hex"], "504b0304")
        self.assertEqual(report["container"]["accepted_schema"], "UNKNOWN")
        self.assertFalse(report["installability"]["installable"])

    def test_rejects_corrupt_zip_and_duplicate_members(self):
        corrupt = self.root / "corrupt.jar"
        corrupt.write_bytes(b"PK\x03\x04broken")
        with self.assertRaisesRegex(PackageInspectionError, "ZIP"):
            inspect_path(corrupt)

        duplicate = self.root / "duplicate.jar"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate, "w") as archive:
                archive.writestr("xlet.properties", self._properties())
                archive.writestr("xlet.properties", self._properties())
        with self.assertRaisesRegex(PackageInspectionError, "duplicate"):
            inspect_path(duplicate)

    def test_report_rendering_is_deterministic_and_path_independent(self):
        report = self._inspect(self._write_layout())
        first = render_json(report)
        second = render_json(report)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), report)
        self.assertNotIn(str(self.root), first)


if __name__ == "__main__":
    unittest.main()
