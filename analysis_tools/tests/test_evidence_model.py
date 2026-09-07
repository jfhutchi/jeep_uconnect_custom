import tempfile
import unittest
from pathlib import Path

from analysis_tools.evidence_model import (
    ACTIVATION_STATES,
    CLASSIFICATIONS,
    validate_activation_ladder,
    validate_evidence,
    write_json,
)


class EvidenceModelTests(unittest.TestCase):
    def test_locked_vocabulary_and_complete_activation_ladder(self):
        self.assertEqual(
            CLASSIFICATIONS,
            ("PROVED", "STRONGLY INFERRED", "UNKNOWN"),
        )
        self.assertEqual(
            ACTIVATION_STATES,
            (
                "class_exists",
                "statically_reachable",
                "activation_mechanism_exists",
                "activation_configured",
                "production_enabled",
                "listener_executable",
                "externally_reachable",
            ),
        )
        ladder = {
            name: {"classification": "UNKNOWN", "evidence": []}
            for name in ACTIVATION_STATES
        }
        validate_activation_ladder(ladder)
        del ladder["externally_reachable"]
        with self.assertRaisesRegex(ValueError, "activation states"):
            validate_activation_ladder(ladder)

    def test_proved_claim_requires_direct_source_reference(self):
        with self.assertRaisesRegex(ValueError, "PROVED.*source"):
            validate_evidence(
                {"classification": "PROVED", "claim": "exists", "sources": []}
            )
        validate_evidence(
            {
                "classification": "PROVED",
                "claim": "parsed",
                "sources": [
                    {
                        "kind": "parsed_structure",
                        "artifact": "resident/app.jar",
                        "member": "example/Test.class",
                        "offset": 4,
                    }
                ],
            }
        )

    def test_proved_claim_rejects_inference_only_source(self):
        with self.assertRaisesRegex(ValueError, "direct source"):
            validate_evidence(
                {
                    "classification": "PROVED",
                    "claim": "runs",
                    "sources": [{"kind": "manual_inference", "artifact": "report"}],
                }
            )

    def test_writer_is_deterministic_and_rejects_absolute_paths(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "out.json"
            write_json(target, {"z": [2, 1], "a": "ok"})
            first = target.read_bytes()
            write_json(target, {"z": [2, 1], "a": "ok"})
            self.assertEqual(first, target.read_bytes())
            self.assertTrue(first.endswith(b"\n"))
            with self.assertRaisesRegex(ValueError, "absolute path"):
                write_json(target, {"input": r"E:\vendor\secret.jar"})
            with self.assertRaisesRegex(ValueError, "absolute path"):
                write_json(target, {"input": "/vendor/secret.jar"})

    def test_writer_sorts_set_like_record_lists(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "out.json"
            write_json(
                target,
                {
                    "records": [
                        {"artifact": "z.jar", "member": "B.class", "offset": 3},
                        {"artifact": "a.jar", "member": "A.class", "offset": 9},
                    ]
                },
            )
            self.assertLess(
                target.read_text(encoding="utf-8").index("a.jar"),
                target.read_text(encoding="utf-8").index("z.jar"),
            )


if __name__ == "__main__":
    unittest.main()
