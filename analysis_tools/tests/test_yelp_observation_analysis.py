import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis_tools"))

import yelp_observation_analysis as analysis


class YelpObservationAnalysisTests(unittest.TestCase):
    def classify(self, **overrides):
        observation = {
            "catalog_scope": "all_pages",
            "tile_state": "enabled",
            "launch_state": "not_attempted",
            "search_state": "not_observed",
            "functionality": "not_observed",
        }
        observation.update(overrides)
        return analysis.analyze_observation(observation, analysis.load_model())

    def test_outcomes_a_through_h(self):
        cases = [
            ({"tile_state": "absent"}, "A"),
            ({"tile_state": "disabled"}, "B"),
            ({"launch_state": "immediate_exit"}, "C"),
            ({"launch_state": "error", "screen_text": "Communication Error Please try again"}, "D"),
            ({"launch_state": "registration"}, "E"),
            ({"launch_state": "home"}, "F"),
            ({"launch_state": "home", "search_state": "results", "functionality": "fully_functional"}, "G"),
            ({"catalog_scope": "partial", "tile_state": "absent"}, "H"),
        ]
        for changes, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(self.classify(**changes)["outcome"], expected)

    def test_error_matching_is_case_insensitive_and_source_bound(self):
        result = self.classify(
            launch_state="error",
            screen_text="SERVICE CURRENTLY NOT AVAILABLE. please try after some time.",
        )
        self.assertEqual(result["outcome"], "D")
        self.assertEqual(result["matched_failure_signatures"], ["service-currently-unavailable"])

    def test_partial_observation_does_not_infer_unobserved_capabilities(self):
        result = self.classify(launch_state="home")
        self.assertNotIn("search succeeded", " ".join(result["established_facts"]).lower())
        self.assertIn("backend acceptance remains unobserved", result["remaining_unknowns"])

    def test_contradictory_and_unknown_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot launch an absent tile"):
            self.classify(tile_state="absent", launch_state="home")
        with self.assertRaisesRegex(ValueError, "unknown field"):
            analysis.analyze_observation({"mystery": True}, analysis.load_model())

    def test_cli_is_canonical_json_in_json_out(self):
        observation = {
            "catalog_scope": "all_pages",
            "tile_state": "enabled",
            "launch_state": "home",
            "search_state": "not_observed",
            "functionality": "not_observed",
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "observation.json"
            source.write_text(json.dumps(observation), encoding="utf-8")
            command = [sys.executable, str(ROOT / "tools" / "analyze_yelp_observation.py"), str(source)]
            first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
            second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(json.loads(first)["outcome"], "F")

    def test_generated_failure_report_is_current(self):
        self.assertEqual(analysis.generate_report(check=True), 0)
        report = json.loads((ROOT / "reports/kim19_runtime_analysis/yelp_failure_signatures.json").read_text())
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual([row["id"] for row in report["signatures"]], sorted(row["id"] for row in report["signatures"]))

    def test_native_predicates_have_exact_sources_and_consumers(self):
        predicates = analysis.load_model()["native_predicates"]
        self.assertEqual(
            [(row["selector"], row["call_site"], row["implementation"], row["field"], row["role"]) for row in predicates],
            [
                ("0x10", "0x125938", "0x10bcbc", "app+0x284", "headless"),
                ("0x0c", "0x125950", "0x10bcf4", "app+0x239", "daemon"),
                ("0x18", "0x125968", "0x10bc4c", "app+0x295", "hasGUI"),
                (None, "0x125978", None, "app+0x4d", "showInHmi"),
            ],
        )
        self.assertTrue(all(row["consumer"] and row["label"] == "PROVED" for row in predicates))

    def test_failure_signatures_are_provenance_bound(self):
        signatures = analysis.load_model()["failure_signatures"]
        required = {"resource", "trigger", "transition", "method_evidence", "interpretation"}
        self.assertTrue(all(required <= row.keys() for row in signatures))
        self.assertTrue(all(row["method_evidence"] and row["match_strings"] for row in signatures))
        report = analysis.build_failure_report(analysis.load_model())
        lifecycle = {"visibility_after", "returns_to_apps", "retry_available"}
        self.assertTrue(all(lifecycle <= row.keys() for row in report["signatures"]))

    def test_source_hash_verification_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.bin"
            path.write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                analysis.verify_source(path, "0" * 64)

    def test_physical_observation_detail_fields_are_preserved_and_classified(self):
        result = analysis.analyze_observation(
            {
                "catalog_scope": "all_pages",
                "yelp_present": True,
                "tile_state": "enabled",
                "launch_attempted": True,
                "splash_seen": True,
                "first_screen_text": "Yelp",
                "error_text": "",
                "remained_open": False,
                "returned_to_apps": True,
                "registration_prompt": False,
                "approx_transition_seconds": 2.5,
                "notes": "One ordinary launch.",
            },
            analysis.load_model(),
        )
        self.assertEqual(result["outcome"], "C")
        self.assertEqual(result["observation"]["approx_transition_seconds"], 2.5)

    def test_detail_fields_reject_bad_types_and_contradictions(self):
        with self.assertRaisesRegex(ValueError, "splash_seen must be boolean or null"):
            analysis.analyze_observation({"splash_seen": "yes"}, analysis.load_model())
        with self.assertRaisesRegex(ValueError, "yelp_present contradicts tile_state"):
            analysis.analyze_observation(
                {"yelp_present": False, "tile_state": "enabled"}, analysis.load_model()
            )
        with self.assertRaisesRegex(ValueError, "nonnegative finite number"):
            analysis.analyze_observation(
                {"approx_transition_seconds": math.nan}, analysis.load_model()
            )


if __name__ == "__main__":
    unittest.main()
