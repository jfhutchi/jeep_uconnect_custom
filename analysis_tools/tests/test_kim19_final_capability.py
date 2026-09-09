import copy
import json
from pathlib import Path
import tempfile
import unittest

from analysis_tools.kim19_final_capability import (
    NOTES,
    REPORT_NAMES,
    build_reports,
    canonical_bytes,
    load_and_validate_notes,
    verify_evidence_inputs,
    write_reports,
)


ROOT = Path(__file__).resolve().parents[2]


class Kim19FinalCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.notes = load_and_validate_notes(NOTES)
        self.evidence = verify_evidence_inputs(self.notes, ROOT)
        self.reports = build_reports(self.notes, self.evidence)

    def test_canonical_bytes_and_exact_report_set(self):
        self.assertEqual(
            canonical_bytes({"z": "caf\u00e9", "a": 1}),
            b'{\n  "a": 1,\n  "z": "caf\\u00e9"\n}\n',
        )
        self.assertEqual(
            REPORT_NAMES,
            ("capability_matrix", "handoff_graph", "unresolved_gates"),
        )
        self.assertEqual(set(self.reports), set(REPORT_NAMES))

    def test_inventory_and_capability_ceiling_are_scope_safe(self):
        matrix = self.reports["capability_matrix"]
        identities = [row["identifier"] for row in matrix["kim19_inventory"]]
        self.assertEqual(len(identities), 9)
        self.assertEqual(len(set(identities)), 9)
        self.assertEqual(len(matrix["jar_inventory"]), 19)
        self.assertEqual(matrix["ceiling"]["highest_proved_kim19_level"], 3)
        self.assertEqual(matrix["ceiling"]["highest_conditional_kim19_level"], 3)
        historical = matrix["historical_conditional"]
        self.assertEqual(historical["candidate"], "SocketCommandSource invoke dispatcher")
        self.assertEqual(historical["level"], 4)
        self.assertEqual(historical["scope"], "archived KIM1/KIM3/KIM12 only; excluded from KIM19")
        self.assertEqual(matrix["decision"]["choice"], "B")
        self.assertEqual(matrix["decision"]["completion_status"], "STATIC RESEARCH COMPLETE")
        for row in matrix["ranked_capabilities"]:
            self.assertIn(row["level"], range(6))

    def test_graph_has_closed_endpoints_evidence_and_required_surfaces(self):
        graph = self.reports["handoff_graph"]
        nodes = {row["id"] for row in graph["nodes"]}
        for edge in graph["edges"]:
            self.assertIn(edge["source"], nodes)
            self.assertIn(edge["target"], nodes)
            self.assertTrue(edge["evidence"])
        self.assertTrue({"input:user", "input:network", "input:media", "input:configuration", "input:vehicle"} <= nodes)
        self.assertTrue({"service:phone", "service:navigation", "service:appmanager", "service:ixc", "service:vsb"} <= nodes)

    def test_every_summary_claim_has_valid_evidence_references(self):
        evidence_ids = {item["id"] for item in self.notes["evidence_inputs"]}
        matrix = self.reports["capability_matrix"]
        gates = self.reports["unresolved_gates"]
        report_groups = {
            group: matrix[group]
            for group in (
                "ranked_capabilities",
                "dynamic_mechanisms",
                "ixc_services",
                "platform_services",
                "scoped_negatives",
            )
        }
        report_groups.update({group: gates[group] for group in ("unknowns", "observations")})

        for group, rows in report_groups.items():
            for index, row in enumerate(rows):
                with self.subTest(group=group, index=index):
                    self.assertTrue(row["evidence"])
                    self.assertLessEqual(set(row["evidence"]), evidence_ids)

        for key in (
            "socket_command_source",
            "historical_conditional",
            "ceiling",
            "decision",
        ):
            with self.subTest(key=key):
                self.assertTrue(matrix[key]["evidence"])
                self.assertLessEqual(set(matrix[key]["evidence"]), evidence_ids)

    def test_observations_cover_a_through_d_with_complete_safety_fields(self):
        gates = self.reports["unresolved_gates"]
        self.assertEqual({row["category"] for row in gates["observations"]}, set("ABCD"))
        required = {
            "action", "visible_states", "proves", "falsifies", "transmits_data",
            "changes_persistent_state", "requires_network", "dependencies", "stop_condition",
        }
        for row in gates["observations"]:
            self.assertTrue(required <= set(row))
        self.assertEqual(gates["recommended_observation"], "B1")

    def test_notes_reject_invalid_labels_duplicate_ids_and_dangling_edges(self):
        bad = copy.deepcopy(self.notes)
        bad["ranked_capabilities"][0]["label"] = "CONFIRMED"
        with self.assertRaisesRegex(ValueError, "label"):
            load_and_validate_notes(data=bad)

        bad = copy.deepcopy(self.notes)
        bad["handoff_edges"][1]["id"] = bad["handoff_edges"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_and_validate_notes(data=bad)

        bad = copy.deepcopy(self.notes)
        bad["handoff_edges"][0]["target"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown node"):
            load_and_validate_notes(data=bad)

        bad = copy.deepcopy(self.notes)
        bad["evidence_bindings"]["ranked_capabilities"]["yelp-ui-services"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown evidence"):
            load_and_validate_notes(data=bad)

        bad = copy.deepcopy(self.notes)
        del bad["evidence_bindings"]["observations"]["A1"]
        with self.assertRaisesRegex(ValueError, "exactly cover observations"):
            load_and_validate_notes(data=bad)

    def test_evidence_inputs_are_hash_bound_and_paths_are_confined(self):
        bad = copy.deepcopy(self.notes)
        bad["evidence_inputs"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "evidence hash mismatch"):
            verify_evidence_inputs(bad, ROOT)
        for path in ("../outside.json", str(ROOT / "README.md")):
            bad = copy.deepcopy(self.notes)
            bad["evidence_inputs"][0]["path"] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "relative"):
                verify_evidence_inputs(bad, ROOT)

    def test_write_and_check_reject_stale_missing_and_unexpected_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_reports(self.reports, output)
            write_reports(self.reports, output, check=True)
            (output / "capability_matrix.json").write_text("{}\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "stale report"):
                write_reports(self.reports, output, check=True)
            write_reports(self.reports, output)
            (output / "handoff_graph.json").unlink()
            with self.assertRaisesRegex(ValueError, "missing report"):
                write_reports(self.reports, output, check=True)
            write_reports(self.reports, output)
            (output / "extra.json").write_text("{}\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "unexpected report"):
                write_reports(self.reports, output, check=True)


if __name__ == "__main__":
    unittest.main()
