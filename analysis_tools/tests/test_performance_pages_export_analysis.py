import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis_tools"))

import performance_pages_export_analysis as analysis
from analysis_tools.tests.test_java_classfile import class_fixture


LABELS = ["PROVED", "INFERRED", "TARGET OBSERVATION REQUIRED", "UNKNOWN"]


def provenance(source_id, *, label="PROVED", binding_ids=None):
    return {
        "label": label,
        "source_ids": [source_id],
        "evidence_binding_ids": list(binding_ids or []),
        "class_function": "example.Export#write",
        "invocation_dataflow": ["caller -> export", "export -> storage"],
        "uncertainty": "None within the recovered static call chain.",
    }


def source(source_id, relative_path, payload):
    return {
        "id": source_id,
        "corpus_relative_path": relative_path,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "description": f"Fixture source {source_id}",
    }


def fixture_jar():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        member = zipfile.ZipInfo("example/Server.class", date_time=(1980, 1, 1, 0, 0, 0))
        member.compress_type = zipfile.ZIP_STORED
        archive.writestr(member, class_fixture())
    return output.getvalue()


def producer_notes(producer_payload=None):
    producer_payload = fixture_jar() if producer_payload is None else producer_payload
    prov = provenance("producer-jar", binding_ids=["run-server-constructor"])
    return {
        "schema_version": 1,
        "scope": "Recovered Performance Pages export producer evidence.",
        "evidence_labels": LABELS,
        "source_artifacts": [
            source("producer-jar", "producer/Export.jar", producer_payload),
        ],
        "class_evidence_selections": [
            {
                "id": "run-server-constructor",
                "source_id": "producer-jar",
                "class_name": "example/Server",
                "class_sha256": hashlib.sha256(class_fixture()).hexdigest(),
                "method_name": "run",
                "descriptor": "()V",
                "instruction_count": 10,
                "selected_instructions": [
                    {
                        "kind": "member",
                        "bci": 8,
                        "opcode": "invokespecial",
                        "owner": "java/net/ServerSocket",
                        "name": "<init>",
                        "descriptor": "(I)V",
                    }
                ],
            }
        ],
        "variants": [
            {
                "id": "z-variant",
                "display_name": "Variant Z",
                "package_id": "example.z",
                "export_role": "producer",
                "provenance": prov,
            },
            {
                "id": "a-variant",
                "display_name": "Variant A",
                "package_id": "example.a",
                "export_role": "producer",
                "provenance": prov,
            },
        ],
        "export_reachability": {
            "status": "statically_gated",
            "entry_point": "Export button action",
            "call_chain": [
                {"operation": "button -> report builder", "provenance": prov},
                {"operation": "report builder -> storage writer", "provenance": prov},
            ],
            "gates": [
                {
                    "id": "media-present",
                    "condition": "Supported removable media is present.",
                    "effect": "The writer can be invoked.",
                    "provenance": prov,
                }
            ],
            "provenance": prov,
        },
        "filename_dataflow": {
            "classification": "system_derived",
            "destination_source": "Storage service selection",
            "path_components": [
                {
                    "order": 2,
                    "component": "fixed extension",
                    "control": "fixed",
                    "transforms": ["append"],
                    "provenance": prov,
                },
                {
                    "order": 1,
                    "component": "timer report identifier",
                    "control": "platform-controlled",
                    "transforms": ["format"],
                    "provenance": prov,
                },
            ],
            "sanitization": ["No independent user filename input is recovered."],
            "collision_behavior": "Unknown in this fixture.",
            "overwrite_behavior": "Unknown in this fixture.",
            "provenance": prov,
        },
        "html_generation": {
            "classification": "fixed_template_runtime_values",
            "template_owner": "Performance Pages",
            "fields": [
                {
                    "id": "elapsed-time",
                    "output_context": "HTML text",
                    "value_source": "Timer model",
                    "control": "vehicle-controlled",
                    "encoding_or_escaping": "Fixed numeric formatter",
                    "provenance": prov,
                }
            ],
            "provenance": prov,
        },
        "failure_signatures": [
            {
                "id": "write-failed",
                "packaged_string": "Export failed",
                "resource_id": "export.failed",
                "caller": "example.Export#write",
                "trigger": "Writer reports failure.",
                "resulting_ui": "A packaged alert is requested.",
                "retry": "No automatic retry is recovered.",
                "partial_file_state": "UNKNOWN",
                "inferred_meaning": "The export did not report success.",
                "provenance": prov,
            }
        ],
        "unresolved_gates": [
            {
                "id": "runtime-media-selection",
                "gate": "Runtime media choice",
                "required_observation": "Benign target observation.",
                "provenance": provenance(
                    "producer-jar",
                    label="TARGET OBSERVATION REQUIRED",
                    binding_ids=["run-server-constructor"],
                ),
            }
        ],
    }


def storage_notes(storage_payload=b"storage evidence"):
    prov = provenance("storage-class")
    unknown = provenance("storage-class", label="UNKNOWN")
    return {
        "schema_version": 1,
        "scope": "Recovered storage and stock consumer evidence.",
        "evidence_labels": LABELS,
        "source_artifacts": [
            source("storage-class", "storage/Storage.class", storage_payload),
        ],
        "class_evidence_selections": [],
        "storage_destinations": [
            {
                "id": "removable-media",
                "medium": "USB or SD selected by the stock service",
                "mount_or_service": "Stock storage service",
                "selection_logic": "Runtime service state",
                "write_scope": "One application report file",
                "provenance": prov,
            }
        ],
        "file_write_capability": {
            "level": 2,
            "title": "Fixed-format export",
            "justification": "The caller selects a report operation, not arbitrary bytes.",
            "limitations": ["No arbitrary path or byte control is proved."],
            "provenance": prov,
        },
        "consumers": [
            {
                "id": "stock-browser",
                "application": "Stock browser",
                "read_behavior": "Contains a static HTML-reading surface.",
                "filename_or_content_match": "No binding to the export is recovered.",
                "static_reference": {"status": "present", "provenance": prov},
                "runtime_reachability": {"status": "unknown", "provenance": unknown},
            }
        ],
        "handoffs": [
            {
                "id": "performance-pages-to-browser",
                "producer": "Performance Pages",
                "storage": "Removable media",
                "consumer": "Stock browser",
                "write_side": {"status": "proved", "provenance": prov},
                "read_side": {"status": "unknown", "provenance": unknown},
                "end_to_end_status": "not_proved",
                "constraints": ["No consumer invocation is recovered."],
                "provenance": unknown,
            }
        ],
        "unresolved_gates": [
            {
                "id": "consumer-binding",
                "gate": "Producer-to-consumer binding",
                "required_observation": "Additional static consumer evidence.",
                "provenance": unknown,
            }
        ],
    }


def write_notes(directory, producer=None, storage=None):
    directory = Path(directory)
    producer_path = directory / "producer.json"
    storage_path = directory / "storage.json"
    producer_path.write_bytes(analysis.canonical_bytes(producer or producer_notes()))
    storage_path.write_bytes(analysis.canonical_bytes(storage or storage_notes()))
    return producer_path, storage_path


class PerformancePagesExportAnalysisTests(unittest.TestCase):
    def test_reports_are_derived_sorted_and_integrity_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            producer_path, storage_path = write_notes(directory)
            reports = analysis.prepare_reports(producer_path, storage_path)

        self.assertEqual(set(reports), set(analysis.REPORT_FILENAMES))
        summary = reports["performance_pages_export_summary.json"]
        self.assertEqual(
            [row["id"] for row in summary["available_variants"]],
            ["a-variant", "z-variant"],
        )
        self.assertEqual(summary["filename_control_classification"], "system_derived")
        self.assertEqual(summary["content_control_classification"], "fixed_template_runtime_values")
        self.assertEqual(summary["file_write_capability"]["level"], 2)
        self.assertEqual(summary["known_consumer_applications"][0]["runtime_reachability"]["status"], "unknown")
        self.assertEqual(summary["potential_write_read_handoffs"][0]["end_to_end_status"], "not_proved")
        self.assertEqual(
            summary["input_sha256"]["producer_notes"],
            hashlib.sha256(analysis.canonical_bytes(producer_notes())).hexdigest(),
        )
        filename_report = reports["performance_pages_filename_dataflow.json"]
        self.assertEqual(
            [row["order"] for row in filename_report["path_components"]], [1, 2]
        )
        self.assertEqual(
            filename_report["source_artifacts"],
            [producer_notes()["source_artifacts"][0]],
        )
        class_report = reports["performance_pages_export_class_evidence.json"]
        self.assertEqual(class_report["bindings"][0]["class_name"], "example/Server")
        self.assertEqual(class_report["bindings"][0]["instruction_count"], 10)
        self.assertEqual(
            class_report["bindings"][0]["source_sha256"],
            producer_notes()["source_artifacts"][0]["sha256"],
        )

    def test_mutating_input_changes_integrity_binding_and_derived_report(self):
        with tempfile.TemporaryDirectory() as directory:
            producer_path, storage_path = write_notes(directory)
            before = analysis.prepare_reports(producer_path, storage_path)
            changed = producer_notes()
            changed["filename_dataflow"]["classification"] = "fixed"
            producer_path.write_bytes(analysis.canonical_bytes(changed))
            after = analysis.prepare_reports(producer_path, storage_path)

        self.assertNotEqual(
            before["performance_pages_export_summary.json"]["input_sha256"],
            after["performance_pages_export_summary.json"]["input_sha256"],
        )
        self.assertEqual(
            after["performance_pages_filename_dataflow.json"]["classification"], "fixed"
        )

    def test_strict_validation_rejects_wrong_labels_unknown_fields_and_duplicate_ids(self):
        bad_label = producer_notes()
        bad_label["variants"][0]["provenance"]["label"] = "ASSUMED"
        with self.assertRaisesRegex(ValueError, "evidence label"):
            analysis.validate_producer_notes(bad_label)

        unknown_field = producer_notes()
        unknown_field["filename_dataflow"]["credential_value"] = "redacted"
        with self.assertRaisesRegex(ValueError, "unknown field"):
            analysis.validate_producer_notes(unknown_field)

        duplicated = producer_notes()
        duplicated["variants"][1]["id"] = duplicated["variants"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate variants id"):
            analysis.validate_producer_notes(duplicated)

    def test_validation_rejects_missing_source_binding_and_static_runtime_conflation(self):
        missing_source = storage_notes()
        missing_source["consumers"][0]["static_reference"]["provenance"]["source_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown source id"):
            analysis.validate_storage_notes(missing_source)

        missing_binding = producer_notes()
        missing_binding["variants"][0]["provenance"]["evidence_binding_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown evidence binding id"):
            analysis.validate_producer_notes(missing_binding)

        conflated = storage_notes()
        conflated["consumers"][0]["runtime_reachability"] = conflated["consumers"][0].pop("static_reference")
        with self.assertRaisesRegex(ValueError, "unknown field|missing field"):
            analysis.validate_storage_notes(conflated)

        unproved_read = storage_notes()
        unproved_read["handoffs"][0]["end_to_end_status"] = "proved"
        unproved_read["handoffs"][0]["provenance"] = provenance("storage-class")
        with self.assertRaisesRegex(ValueError, "without both proved sides"):
            analysis.validate_storage_notes(unproved_read)

    def test_strict_json_rejects_duplicate_keys_and_nonstandard_numbers(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            analysis.strict_json_loads('{"scope":"one","scope":"two"}')
        with self.assertRaisesRegex(ValueError, "numeric constant"):
            analysis.strict_json_loads('{"schema_version":NaN}')

    def test_corpus_hash_verification_detects_mutation_and_rejects_unsafe_paths(self):
        producer = producer_notes()
        storage = storage_notes()
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            producer_source = corpus / "producer" / "Export.jar"
            storage_source = corpus / "storage" / "Storage.class"
            producer_source.parent.mkdir()
            storage_source.parent.mkdir()
            producer_source.write_bytes(fixture_jar())
            storage_source.write_bytes(b"storage evidence")
            analysis.verify_corpus_sources(corpus, producer, storage)
            storage_source.write_bytes(b"mutated")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                analysis.verify_corpus_sources(corpus, producer, storage)

        unsafe = producer_notes()
        unsafe["source_artifacts"][0]["corpus_relative_path"] = "../outside.bin"
        with self.assertRaisesRegex(ValueError, "safe corpus-relative path"):
            analysis.validate_producer_notes(unsafe)

    def test_corpus_class_evidence_rejects_mutated_bci_and_member_tuple(self):
        producer = producer_notes()
        storage = storage_notes()
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            (corpus / "producer").mkdir()
            (corpus / "storage").mkdir()
            (corpus / "producer" / "Export.jar").write_bytes(fixture_jar())
            (corpus / "storage" / "Storage.class").write_bytes(b"storage evidence")
            analysis.verify_corpus_sources(corpus, producer, storage)

            wrong_bci = copy.deepcopy(producer)
            wrong_bci["class_evidence_selections"][0]["selected_instructions"][0]["bci"] = 7
            with self.assertRaisesRegex(ValueError, "selected instruction mismatch"):
                analysis.verify_corpus_sources(corpus, wrong_bci, storage)

            wrong_member = copy.deepcopy(producer)
            wrong_member["class_evidence_selections"][0]["selected_instructions"][0]["name"] = "accept"
            with self.assertRaisesRegex(ValueError, "selected instruction mismatch"):
                analysis.verify_corpus_sources(corpus, wrong_member, storage)

    def test_corpus_sources_are_hashed_and_parsed_from_the_same_bytes(self):
        producer = producer_notes()
        storage = storage_notes()
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            (corpus / "producer").mkdir()
            (corpus / "storage").mkdir()
            jar_path = (corpus / "producer" / "Export.jar").resolve()
            jar_path.write_bytes(fixture_jar())
            (corpus / "storage" / "Storage.class").write_bytes(b"storage evidence")
            actual_zip_file = zipfile.ZipFile

            def bytes_only_zip_file(source, *args, **kwargs):
                self.assertIsInstance(source, io.BytesIO)
                return actual_zip_file(source, *args, **kwargs)

            with mock.patch.object(
                analysis.zipfile, "ZipFile", side_effect=bytes_only_zip_file
            ):
                analysis.verify_corpus_sources(corpus, producer, storage)

    def test_report_directory_inside_corpus_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus"
            (corpus / "producer").mkdir(parents=True)
            (corpus / "storage").mkdir()
            (corpus / "producer" / "Export.jar").write_bytes(fixture_jar())
            (corpus / "storage" / "Storage.class").write_bytes(b"storage evidence")
            producer_path, storage_path = write_notes(root)
            report_dir = corpus / "generated-reports"
            with self.assertRaisesRegex(ValueError, "report directory must be outside corpus"):
                analysis.generate_reports(
                    producer_path,
                    storage_path,
                    report_dir,
                    corpus=corpus,
                )
            self.assertFalse(report_dir.exists())

    def test_generate_then_check_is_canonical_and_stale_check_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            producer_path, storage_path = write_notes(root)
            report_dir = root / "reports"
            self.assertEqual(
                analysis.generate_reports(producer_path, storage_path, report_dir), 0
            )
            initial = {path.name: path.read_bytes() for path in report_dir.iterdir()}
            self.assertEqual(
                analysis.generate_reports(
                    producer_path, storage_path, report_dir, check=True
                ),
                0,
            )
            stale_path = report_dir / "performance_pages_html_fields.json"
            stale_path.write_bytes(b"{}\n")
            self.assertEqual(
                analysis.generate_reports(
                    producer_path, storage_path, report_dir, check=True
                ),
                1,
            )
            self.assertEqual(stale_path.read_bytes(), b"{}\n")
            self.assertTrue(all(payload.endswith(b"\n") for payload in initial.values()))
            self.assertTrue(all(payload.decode("ascii") for payload in initial.values()))

    def test_cli_is_deterministic_and_supports_check_and_corpus_rehash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus"
            (corpus / "producer").mkdir(parents=True)
            (corpus / "storage").mkdir()
            (corpus / "producer" / "Export.jar").write_bytes(fixture_jar())
            (corpus / "storage" / "Storage.class").write_bytes(b"storage evidence")
            producer_path, storage_path = write_notes(root)
            report_dir = root / "reports"
            command = [
                sys.executable,
                str(ROOT / "tools" / "analyze_performance_pages_export.py"),
                "--producer-notes",
                str(producer_path),
                "--storage-notes",
                str(storage_path),
                "--report-dir",
                str(report_dir),
                "--corpus",
                str(corpus),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            first = {path.name: path.read_bytes() for path in report_dir.iterdir()}
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            second = {path.name: path.read_bytes() for path in report_dir.iterdir()}
            checked = subprocess.run(
                [*command, "--check"], cwd=ROOT, check=False, capture_output=True
            )

        self.assertEqual(first, second)
        self.assertEqual(checked.returncode, 0, checked.stderr.decode())


if __name__ == "__main__":
    unittest.main()
