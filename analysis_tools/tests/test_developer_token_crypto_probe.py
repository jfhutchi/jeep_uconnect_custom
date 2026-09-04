import base64
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
import hashlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa, padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID

import analysis_tools.developer_token_crypto_probe as probe


class DeveloperTokenCryptoProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
        cls.public_key = cls.private_key.public_key()
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Fixture Signer")])
        cls.certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(cls.public_key)
            .serial_number(1)
            .not_valid_before(datetime(2020, 1, 1))
            .not_valid_after(datetime(2030, 1, 1))
            .sign(cls.private_key, hashes.SHA256())
        )

    def _require(self, name: str):
        value = getattr(probe, name, None)
        self.assertTrue(callable(value), f"{name} must be implemented")
        return value

    def test_parses_escaped_java_properties_token_without_echoing_invalid_input(self) -> None:
        parse_token = self._require("parse_developer_token")
        token = bytes(range(64))
        encoded = base64.b64encode(token).decode("ascii").replace("=", r"\=")

        self.assertEqual(
            parse_token(f"xlet.name=Fixture\nxlet.developerToken={encoded}\n".encode()),
            token,
        )

        secret = "DO_NOT_ECHO_INVALID_TOKEN"
        with self.assertRaises(getattr(probe, "ProbeError")) as context:
            parse_token(f"xlet.developerToken={secret}\n".encode())
        self.assertNotIn(secret, str(context.exception))

    def test_recognizes_pkcs1_v1_5_sha256_digest_info(self) -> None:
        recover = self._require("rsa_public_recover")
        classify = self._require("classify_pkcs1_v1_5")
        message = b"signed descriptor fixture"
        signature = self.private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())

        recovery = recover(signature, self.public_key)
        classification = classify(recovery.encoded_message)

        self.assertEqual(recovery.status, "recovered")
        self.assertTrue(classification.valid)
        self.assertEqual(classification.block_type, 1)
        self.assertEqual(classification.digest_algorithm, "sha256")
        self.assertEqual(classification.digest_length, 32)

    def test_pkcs1_type_two_block_is_not_counted_as_a_signature_match(self) -> None:
        make_candidate = self._require("make_candidate")
        build_summary = self._require("build_summary")
        message = b"fixture payload"
        digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256(
            message
        ).digest()
        modulus_bytes = self.private_key.key_size // 8
        encoded = (
            b"\x00\x02"
            + b"\x7f" * (modulus_bytes - len(digest_info) - 3)
            + b"\x00"
            + digest_info
        )
        numbers = self.private_key.private_numbers()
        token = pow(
            int.from_bytes(encoded, "big"),
            numbers.d,
            numbers.public_numbers.n,
        ).to_bytes(modulus_bytes, "big")
        candidate = make_candidate(self.public_key, "keys/fixture.pub")

        summary = build_summary(token, [candidate], [message])

        self.assertEqual(summary["pkcs1_v1_5"]["valid_blocks"], 1)
        self.assertEqual(summary["pkcs1_v1_5"]["classified"][0]["block_type"], 2)
        self.assertEqual(summary["verification"]["matches"], 0)

    def test_verification_attempts_count_only_executed_hash_scheme_pairs(self) -> None:
        make_candidate = self._require("make_candidate")
        build_summary = self._require("build_summary")
        message = b"attempt accounting fixture"
        token = self.private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        candidate = make_candidate(self.public_key, "keys/fixture.pub")

        summary = build_summary(token, [candidate], [message])

        # PKCS#1 v1.5 supports six configured digests. PSS tests every
        # configured message-digest/MGF1-digest pairing.
        expected_per_recovery = 6 + (6 * 6)
        self.assertGreater(summary["recovery"]["length_compatible"], 0)
        self.assertEqual(
            summary["verification"]["attempts"],
            summary["recovery"]["length_compatible"] * expected_per_recovery,
        )
        self.assertEqual(summary["verification"]["matches"], 1)
        self.assertEqual(
            summary["verification"]["matched_algorithms"],
            [
                {
                    "spki_sha256": candidate.spki_sha256,
                    "variant": "as_stored",
                    "scheme": "pkcs1_v1_5",
                    "digest_algorithm": "sha256",
                }
            ],
        )

    def test_recognizes_pss_sha256_structure_and_salt_length(self) -> None:
        recover = self._require("rsa_public_recover")
        classify = self._require("classify_pss")
        signature = self.private_key.sign(
            b"PSS fixture",
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
            hashes.SHA256(),
        )

        recovery = recover(signature, self.public_key)
        classification = classify(recovery.encoded_message, 2_048, "sha256")

        self.assertTrue(classification.valid)
        self.assertEqual(classification.digest_algorithm, "sha256")
        self.assertEqual(classification.salt_length, 32)
        self.assertTrue(classification.canonical_salt)

    def test_recognizes_and_matches_pss_with_independent_mgf1_digest(self) -> None:
        recover = self._require("rsa_public_recover")
        classify = self._require("classify_pss")
        make_candidate = self._require("make_candidate")
        build_summary = self._require("build_summary")
        message = b"PSS independent MGF1 fixture"
        signature = self.private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA1()), salt_length=32),
            hashes.SHA256(),
        )

        recovery = recover(signature, self.public_key)
        same_digest = classify(recovery.encoded_message, 2_048, "sha256")
        independent_digest = classify(
            recovery.encoded_message,
            2_048,
            "sha256",
            "sha1",
        )

        self.assertFalse(same_digest.valid)
        self.assertTrue(independent_digest.valid)
        self.assertEqual(independent_digest.digest_algorithm, "sha256")
        self.assertEqual(independent_digest.mgf_algorithm, "sha1")

        candidate = make_candidate(self.public_key, "keys/fixture.pub")
        summary = build_summary(signature, [candidate], [message])
        self.assertEqual(summary["verification"]["matches"], 1)
        self.assertEqual(
            summary["verification"]["matched_algorithms"],
            [
                {
                    "spki_sha256": candidate.spki_sha256,
                    "variant": "as_stored",
                    "scheme": "pss",
                    "digest_algorithm": "sha256",
                    "mgf_algorithm": "sha1",
                }
            ],
        )

    def test_rejects_signature_integer_at_or_above_modulus(self) -> None:
        recover = self._require("rsa_public_recover")
        numbers = self.public_key.public_numbers()
        signature = numbers.n.to_bytes(256, "big")

        recovery = recover(signature, self.public_key)

        self.assertEqual(recovery.status, "integer_ge_modulus")
        self.assertIsNone(recovery.encoded_message)

    def test_deduplicates_candidates_by_spki_and_sorts_sources(self) -> None:
        make_candidate = self._require("make_candidate")
        deduplicate = self._require("deduplicate_candidates")
        first = make_candidate(self.public_key, "z/key.pub")
        second = make_candidate(self.public_key, "a/key.pub", certificate=self.certificate)

        candidates = deduplicate([first, second])

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].sources, ("a/key.pub", "z/key.pub"))
        self.assertEqual(len(candidates[0].certificate_sha256), 1)
        self.assertIn("CN=Fixture Signer", candidates[0].subjects)

    def test_rejects_absolute_or_parent_candidate_sources(self) -> None:
        make_candidate = self._require("make_candidate")

        for source in ("../escape.pub", "/absolute/key.pub", "C:/absolute/key.pub"):
            with self.subTest(source=source):
                with self.assertRaises(getattr(probe, "ProbeError")):
                    make_candidate(self.public_key, source)

    def test_enumerates_pkcs7_signer_certificate_from_jar(self) -> None:
        enumerate_certificates = self._require("enumerate_jar_signer_certificates")
        signature_block = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"fixture manifest")
            .add_signer(self.certificate, self.private_key, hashes.SHA256())
            .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary])
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jar_path = root / "apps" / "key.jar"
            jar_path.parent.mkdir()
            with zipfile.ZipFile(jar_path, "w") as archive:
                archive.writestr("META-INF/FIXTURE.RSA", signature_block)

            candidates = enumerate_certificates(jar_path, root)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].sources,
            ("apps/key.jar!/META-INF/FIXTURE.RSA",),
        )
        self.assertIn("CN=Fixture Signer", candidates[0].subjects)

    def test_legacy_ssh1_rsa_falls_back_after_unsupported_ssh_loader(self) -> None:
        enumerate_key = self._require("enumerate_public_key_file")
        numbers = self.public_key.public_numbers()
        payload = f"2048 {numbers.e} {numbers.n} fixture\n".encode("ascii")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "keys" / "ssh_host_key.pub"
            key_path.parent.mkdir()
            key_path.write_bytes(payload)
            try:
                candidates = enumerate_key(key_path, root)
            except Exception as error:  # pragma: no cover - makes the regression explicit
                self.fail(f"legacy SSH1 key must reach the fallback parser: {type(error).__name__}")

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].key_type, "rsa")
        self.assertEqual(candidates[0].bits, 2_048)

    def test_malformed_ssh1_numeric_key_fails_with_a_sanitized_probe_error(self) -> None:
        enumerate_key = self._require("enumerate_public_key_file")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "keys" / "malformed.pub"
            key_path.parent.mkdir()
            key_path.write_bytes(b"8 2 251 SECRET_SSH_COMMENT\n")

            with self.assertRaises(getattr(probe, "ProbeError")) as caught:
                enumerate_key(key_path, root)

        self.assertEqual(
            str(caught.exception),
            "SSH1 public-key input has invalid numeric fields",
        )
        self.assertNotIn("SECRET_SSH_COMMENT", str(caught.exception))

    def test_public_key_enumeration_does_not_emit_crypto_warnings(self) -> None:
        enumerate_key = self._require("enumerate_public_key_file")
        dsa_public = dsa.generate_private_key(key_size=1_024).public_key()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            payload = dsa_public.public_bytes(
                serialization.Encoding.OpenSSH,
                serialization.PublicFormat.OpenSSH,
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "keys" / "legacy_dsa.pub"
            key_path.parent.mkdir()
            key_path.write_bytes(payload)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                candidates = enumerate_key(key_path, root)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].key_type, "dsa")
        self.assertEqual(caught, [])

    def test_summary_is_deterministic_and_never_contains_secret_material(self) -> None:
        make_candidate = self._require("make_candidate")
        build_summary = self._require("build_summary")
        render_summary = self._require("render_summary")
        token = (b"SENSITIVE_TOKEN_BYTES_" * 13)[:256].ljust(256, b"!")
        candidate = make_candidate(
            self.public_key,
            "keys/fixture.pub",
            certificate=self.certificate,
        )
        message = b"prodIdPath=/sensitive AUTH_KEY_VALUE=do-not-print"

        summary = build_summary(token, [candidate], [message])
        json_output = render_summary(summary, "json")
        text_output = render_summary(summary, "text")

        self.assertEqual(json_output, render_summary(summary, "json"))
        parsed = json.loads(json_output)
        self.assertEqual(
            parsed["token"],
            {"byte_length": 256, "sha256": hashlib.sha256(token).hexdigest()},
        )
        combined = json_output + text_output
        forbidden = (
            token.hex(),
            base64.b64encode(token).decode("ascii"),
            message.decode("ascii"),
            self.public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("ascii"),
            str(self.public_key.public_numbers().n),
            format(self.public_key.public_numbers().n, "x"),
        )
        for value in forbidden:
            self.assertNotIn(value, combined)
        self.assertNotIn("BEGIN PUBLIC KEY", combined)
        self.assertNotIn("AUTH_KEY_VALUE", combined)
        self.assertNotIn("prodIdPath", combined)

    def test_certificate_subject_controls_are_escaped_in_all_output_formats(self) -> None:
        make_candidate = self._require("make_candidate")
        build_summary = self._require("build_summary")
        render_summary = self._require("render_summary")
        unsafe_name = x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, "Fixture\nInjected\x1b[31m")]
        )
        unsafe_certificate = (
            x509.CertificateBuilder()
            .subject_name(unsafe_name)
            .issuer_name(unsafe_name)
            .public_key(self.public_key)
            .serial_number(2)
            .not_valid_before(datetime(2020, 1, 1))
            .not_valid_after(datetime(2030, 1, 1))
            .sign(self.private_key, hashes.SHA256())
        )
        candidate = make_candidate(
            self.public_key,
            "keys/unsafe-subject.pem",
            certificate=unsafe_certificate,
        )
        summary = build_summary(b"opaque token", [candidate])
        combined = render_summary(summary, "json") + render_summary(summary, "text")

        self.assertNotIn("\x1b", combined)
        self.assertNotIn("Fixture\nInjected", combined)
        self.assertIn(r"\u000a", combined)
        self.assertIn(r"\u001b", combined)

    def test_summary_rejects_nonbyte_messages_with_a_sanitized_error(self) -> None:
        build_summary = self._require("build_summary")

        with self.assertRaises(getattr(probe, "ProbeError")) as caught:
            build_summary(b"token", [], ["SECRET_MESSAGE_VALUE"])

        self.assertNotIn("SECRET_MESSAGE_VALUE", str(caught.exception))

    def test_argument_parser_requires_explicit_corpus_and_descriptor(self) -> None:
        build_parser = self._require("build_argument_parser")
        parser = build_parser()

        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args([])
        args = parser.parse_args(
            [
                "--corpus-root",
                "corpus",
                "--token-descriptor",
                "descriptor.properties",
            ]
        )
        self.assertEqual(args.corpus_root, Path("corpus"))
        self.assertEqual(args.token_descriptor, [Path("descriptor.properties")])

    def test_missing_crypto_dependency_fails_with_a_sanitized_probe_error(self) -> None:
        secret = "SECRET_DEPENDENCY_DETAIL"

        with mock.patch.object(probe, "_CRYPTO_IMPORT_ERROR", ImportError(secret)):
            with self.assertRaises(getattr(probe, "ProbeError")) as caught:
                probe.rsa_public_recover(b"opaque", self.public_key)

        self.assertEqual(str(caught.exception), "the cryptography dependency is required")
        self.assertNotIn(secret, str(caught.exception))

    def test_cli_fails_loudly_and_safely_for_a_missing_corpus(self) -> None:
        stdout = StringIO()
        stderr = StringIO()
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "SECRET_PATH_COMPONENT" / "missing"
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = probe.main(
                    [
                        "--corpus-root",
                        str(missing),
                        "--token-descriptor",
                        "descriptor.properties",
                    ]
                )

        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "error: corpus root does not exist\n")
        self.assertNotIn("SECRET_PATH_COMPONENT", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
