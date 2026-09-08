import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from analysis_tools.java_classfile import parse_class
from analysis_tools.kim19_yelp_analysis import (
    LABELS,
    REPORT_NAMES,
    build_reports,
    canonical_bytes,
    load_sources,
    validate_java_site,
    validate_notes,
    verify_outputs,
    write_outputs,
)
from analysis_tools.tests.test_java_classfile import class_fixture


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class Kim19YelpAnalysisTests(unittest.TestCase):
    def make_fixture(self, root: Path):
        descriptor = b"xlet.appId=test-app\nxlet.mainClass=example.Server\n"
        key = b"synthetic-key-jar"
        jar_path = root / "yelp.jar"
        with zipfile.ZipFile(jar_path, "w") as archive:
            archive.writestr("example/Server.class", class_fixture())
            archive.writestr("xlet.properties", descriptor)
            archive.writestr("yelp.properties", "places_api_base=https://example.invalid/search\n")
        for name, data in (("xlet.properties", descriptor), ("key.jar", key)):
            (root / name).write_bytes(data)
        return {
            "descriptor": {"path": "xlet.properties", "size": len(descriptor), "sha256": sha256(descriptor)},
            "key_jar": {"path": "key.jar", "size": len(key), "sha256": sha256(key)},
            "yelp_jar": {"path": "yelp.jar", "size": jar_path.stat().st_size,
                         "sha256": sha256(jar_path.read_bytes())},
        }

    def minimal_notes(self, sources):
        reports = {
            "launch_graph": {
                "nodes": [{"id": "ui", "label": "PROVED"}, {"id": "socket", "label": "UNKNOWN"}],
                "edges": [{
                    "id": "construct", "source": "ui", "target": "socket", "label": "PROVED",
                    "evidence": [{
                        "class": "example/Server", "method": "run", "descriptor": "()V", "bci": 8,
                        "opcode": "invokespecial", "owner": "java/net/ServerSocket", "name": "<init>",
                        "callee_descriptor": "(I)V",
                    }],
                }],
            },
            "runtime_gates": {"gates": []},
            "input_dataflow": {"flows": []},
            "network_fields": {"fields": []},
            "response_actions": {"actions": []},
            "failure_paths": {"paths": []},
            "stock_handoffs": {"handoffs": []},
        }
        return {
            "format": "kim19-yelp-reviewed-notes-v1",
            "labels": sorted(LABELS),
            "app": {"app_id": "test-app", "name": "Yelp", "version": "1",
                    "main_class": "example/Server"},
            "sources": sources,
            "prior_evidence": [],
            "reports": reports,
        }

    def test_canonical_bytes_are_sorted_ascii_lf(self):
        self.assertEqual(canonical_bytes({"z": "caf\u00e9", "a": 1}),
                         b'{\n  "a": 1,\n  "z": "caf\\u00e9"\n}\n')

    def test_load_sources_hashes_members_and_detects_later_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = self.minimal_notes(self.make_fixture(root))
            sources = load_sources(root, notes)
            self.assertIn("example/Server", sources.classes)
            self.assertEqual(sources.classes["example/Server"].name, "example/Server")
            sources.assert_unchanged()
            (root / "xlet.properties").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "source changed"):
                sources.assert_unchanged()

    def test_load_sources_rejects_unsafe_missing_and_hash_mismatched_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = self.make_fixture(root)
            for key, value in (("path", "../escape"), ("path", "missing"), ("sha256", "0" * 64)):
                notes = self.minimal_notes(copy.deepcopy(sources))
                notes["sources"]["descriptor"][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    load_sources(root, notes)

    def test_java_site_binds_exact_method_instruction_and_callee(self):
        classes = {"example/Server": parse_class(class_fixture())}
        site = self.minimal_notes({})["reports"]["launch_graph"]["edges"][0]["evidence"][0]
        bound = validate_java_site(site, classes)
        self.assertEqual(bound["bci"], 8)
        self.assertEqual(bound["owner"], "java/net/ServerSocket")
        self.assertEqual(bound["callee_descriptor"], "(I)V")

    def test_java_site_rejects_every_mismatched_identity_component(self):
        classes = {"example/Server": parse_class(class_fixture())}
        site = self.minimal_notes({})["reports"]["launch_graph"]["edges"][0]["evidence"][0]
        mutations = {
            "class": "example/Missing", "method": "missing", "descriptor": "(I)V", "bci": 7,
            "opcode": "invokevirtual", "owner": "java/net/Socket", "name": "open",
            "callee_descriptor": "()V",
        }
        for key, value in mutations.items():
            changed = dict(site)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_java_site(changed, classes)

    def test_notes_require_exact_labels_report_set_and_unique_graph_ids(self):
        notes = self.minimal_notes({})
        validate_notes(notes)
        for mutation in ("label", "report", "duplicate_node", "unknown_node", "duplicate_edge"):
            changed = copy.deepcopy(notes)
            if mutation == "label":
                changed["reports"]["launch_graph"]["nodes"][0]["label"] = "CONFIRMED"
            elif mutation == "report":
                del changed["reports"]["failure_paths"]
            elif mutation == "duplicate_node":
                changed["reports"]["launch_graph"]["nodes"].append(
                    changed["reports"]["launch_graph"]["nodes"][0])
            elif mutation == "unknown_node":
                changed["reports"]["launch_graph"]["edges"][0]["target"] = "missing"
            else:
                changed["reports"]["launch_graph"]["edges"].append(
                    changed["reports"]["launch_graph"]["edges"][0])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_notes(changed)

    def test_notes_reject_public_authorization_values_but_allow_hash_metadata(self):
        notes = self.minimal_notes({})
        notes["reports"]["network_fields"]["fields"].append({
            "id": "authorization", "label": "PROVED", "value_sha256": "0" * 64,
            "public_value": "REDACTED", "control": "application",
        })
        validate_notes(notes)
        notes["reports"]["network_fields"]["fields"][0]["public_value"] = "Basic abc123"
        with self.assertRaisesRegex(ValueError, "credential"):
            validate_notes(notes)

    def test_build_reports_binds_sites_and_emits_exact_seven_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = self.minimal_notes(self.make_fixture(root))
            sources = load_sources(root, notes)
            reports = build_reports(notes, sources)
            self.assertEqual(set(reports), set(REPORT_NAMES))
            evidence = reports["launch_graph"]["edges"][0]["evidence"][0]
            self.assertEqual(evidence["bci"], 8)
            self.assertEqual(evidence["source_jar_sha256"], notes["sources"]["yelp_jar"]["sha256"])
            self.assertEqual(canonical_bytes(reports), canonical_bytes(build_reports(notes, sources)))

    def test_write_and_check_reject_stale_missing_and_extra_outputs(self):
        reports = {name: {"format": "test", "report": name} for name in REPORT_NAMES}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_outputs(reports, output)
            verify_outputs(reports, output)
            first = output / f"{REPORT_NAMES[0]}.json"
            first.write_text("{}\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "stale report"):
                verify_outputs(reports, output)
            write_outputs(reports, output)
            (output / "extra.json").write_text("{}\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "unexpected report"):
                verify_outputs(reports, output)

    def test_report_lists_are_canonicalized_by_id_without_mutating_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = self.minimal_notes(self.make_fixture(root))
            notes["reports"]["runtime_gates"]["gates"] = [
                {"id": "z", "label": "UNKNOWN"}, {"id": "a", "label": "PROVED"},
            ]
            original = copy.deepcopy(notes)
            reports = build_reports(notes, load_sources(root, notes))
            self.assertEqual([row["id"] for row in reports["runtime_gates"]["gates"]], ["a", "z"])
            self.assertEqual(notes, original)


if __name__ == "__main__":
    unittest.main()
