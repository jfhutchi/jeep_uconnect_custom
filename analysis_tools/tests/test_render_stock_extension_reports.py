import tempfile
import unittest
from pathlib import Path

from analysis_tools.evidence_model import ACTIVATION_STATES
from analysis_tools.render_stock_extension_reports import (
    REQUIRED_CANDIDATE_FIELDS,
    render_reports,
    validate_ledger,
)


def source(kind="parsed_structure"):
    return {
        "kind": kind,
        "artifact": "resident/example.jar",
        "member": "example/Entry.class",
        "offset": 4,
    }


def candidate(rank):
    return {
        "rank": rank,
        "component": f"Component {rank}",
        "activation_path": "resident lifecycle -> dispatcher",
        "user_controlled_input": "bounded input",
        "useful_resulting_capability": "bounded resident capability",
        "prerequisites": ["resident component active"],
        "evidence_classification": "PROVED" if rank == 1 else "STRONGLY INFERRED",
        "unresolved_unknowns": ["runtime observation"],
        "new_package_authorization_required": "no" if rank == 1 else "unknown",
        "sources": [source()],
    }


def ledger():
    ladder = {
        state: {
            "classification": "PROVED" if state in (
                "class_exists", "statically_reachable",
                "activation_mechanism_exists",
            ) else "UNKNOWN",
            "conclusion": "direct structural evidence" if state in (
                "class_exists", "statically_reachable",
                "activation_mechanism_exists",
            ) else "not established",
            "sources": [source()] if state in (
                "class_exists", "statically_reachable",
                "activation_mechanism_exists",
            ) else [],
        }
        for state in ACTIVATION_STATES
    }
    return {
        "schema_version": 1,
        "corpus": {
            "summary": "Recovered resident Java and candidate-led native metadata",
            "coverage": "300 archives; synthetic fixture ledger",
        },
        "socket_command_source": {
            "verdict_classification": "STRONGLY INFERRED",
            "verdict": "Lifecycle-activatable local test surface; target execution unproved.",
            "activation_ladder": ladder,
        },
        "network_endpoints": [
            {
                "component": "Component 1",
                "endpoint": "127.0.0.1:11111",
                "behavior": "line-framed local listener",
                "classification": "PROVED",
                "unknowns": ["target bind success"],
                "sources": [source()],
            }
        ],
        "input_surfaces": [
            {
                "origin": "loopback client",
                "signed_component": "Component 1",
                "parser_dispatcher": "line reader -> JSON dispatcher",
                "capability": "resident UI test actions",
                "classification": "STRONGLY INFERRED",
                "missing_links": ["target runtime observation"],
                "sources": [source()],
            }
        ],
        "candidates": [candidate(rank) for rank in range(1, 6)],
    }


class RenderStockExtensionReportsTests(unittest.TestCase):
    def test_exactly_five_contract_and_required_fields_are_locked(self):
        self.assertEqual(
            REQUIRED_CANDIDATE_FIELDS,
            {
                "rank", "component", "activation_path",
                "user_controlled_input", "useful_resulting_capability",
                "prerequisites", "evidence_classification",
                "unresolved_unknowns", "new_package_authorization_required",
            },
        )
        validate_ledger(ledger())

    def test_renderer_creates_exact_required_reports_deterministically(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            render_reports(ledger(), first)
            render_reports(ledger(), second)
            first_files = {path.name: path.read_bytes() for path in first.iterdir()}
            second_files = {path.name: path.read_bytes() for path in second.iterdir()}
            self.assertEqual(first_files, second_files)
            self.assertEqual(
                set(first_files),
                {
                    "stock_extension_surface.md",
                    "resident_network_services.md",
                    "user_controlled_input_surface.md",
                },
            )
            controlling = first_files["stock_extension_surface.md"].decode()
            self.assertEqual(controlling.count("### Rank "), 5)
            for classification in ("PROVED", "STRONGLY INFERRED", "UNKNOWN"):
                self.assertIn(classification, controlling)
            for state in ACTIVATION_STATES:
                self.assertIn(state.replace("_", " ").title(), controlling)

    def test_rejects_candidate_count_missing_fields_and_bad_authorization_value(self):
        data = ledger()
        data["candidates"].pop()
        with self.assertRaisesRegex(ValueError, "exactly five"):
            validate_ledger(data)
        data = ledger()
        del data["candidates"][0]["activation_path"]
        with self.assertRaisesRegex(ValueError, "candidate fields"):
            validate_ledger(data)
        data = ledger()
        data["candidates"][0]["new_package_authorization_required"] = "maybe"
        with self.assertRaisesRegex(ValueError, "authorization"):
            validate_ledger(data)

    def test_rejects_proved_inference_absolute_paths_and_payload_fields(self):
        data = ledger()
        data["candidates"][0]["sources"] = [source("manual_inference")]
        with self.assertRaisesRegex(ValueError, "direct source"):
            validate_ledger(data)
        data = ledger()
        data["corpus"]["coverage"] = r"E:\vendor\corpus"
        with self.assertRaisesRegex(ValueError, "absolute path"):
            validate_ledger(data)
        data = ledger()
        data["binary_payload"] = "AAECAwQ="
        with self.assertRaisesRegex(ValueError, "payload"):
            validate_ledger(data)

    def test_rejects_static_presence_promoted_to_execution_and_bypass_recommendations(self):
        data = ledger()
        data["socket_command_source"]["activation_ladder"]["listener_executable"] = {
            "classification": "PROVED",
            "conclusion": "listener executes",
            "sources": [source("constant_pool_presence")],
        }
        with self.assertRaisesRegex(ValueError, "direct source"):
            validate_ledger(data)
        data = ledger()
        data["candidates"][0]["activation_path"] = "Recommended authentication bypass"
        with self.assertRaisesRegex(ValueError, "prohibited recommendation"):
            validate_ledger(data)


if __name__ == "__main__":
    unittest.main()
