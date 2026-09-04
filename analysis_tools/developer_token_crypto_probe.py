"""Read-only cryptographic classification for opaque developer-token metadata.

The probe deliberately emits only hashes, public certificate/key metadata, safe
relative source names, and aggregate verification results. Secret-bearing input
bytes never enter an exception message or rendered report.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
from typing import Any, Iterable, Sequence
import warnings
import zipfile

_CRYPTO_IMPORT_ERROR: ImportError | None = None
try:
    from cryptography import x509
    from cryptography.exceptions import UnsupportedAlgorithm
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import dsa, ec, rsa
    from cryptography.hazmat.primitives.serialization import pkcs7
    from cryptography.utils import CryptographyDeprecationWarning
except ImportError as error:  # pragma: no cover - exercised on dependency-free hosts
    _CRYPTO_IMPORT_ERROR = error


class ProbeError(ValueError):
    """Raised when an input is missing, unsafe, or structurally invalid."""


@dataclass(frozen=True)
class RecoveryResult:
    status: str
    modulus_bits: int
    encoded_message: bytes | None = field(default=None, repr=False)


@dataclass(frozen=True)
class Pkcs1Classification:
    valid: bool
    block_type: int | None = None
    padding_bytes: int | None = None
    payload_length: int | None = None
    digest_algorithm: str | None = None
    digest_length: int | None = None
    raw_digest_length: int | None = None
    _digest: bytes | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class PssClassification:
    valid: bool
    digest_algorithm: str
    mgf_algorithm: str
    salt_length: int | None = None
    canonical_salt: bool = False
    _encoded_hash: bytes | None = field(default=None, repr=False, compare=False)
    _salt: bytes | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class CandidateKey:
    public_key: Any = field(repr=False, compare=False)
    spki_sha256: str
    key_type: str
    bits: int
    sources: tuple[str, ...]
    certificate_sha256: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()


_HASH_NAMES = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512")
_PSS_HASH_NAMES = _HASH_NAMES
_PSS_MGF_HASH_NAMES = _HASH_NAMES
_DIGEST_INFO_PREFIXES = {
    "md5": bytes.fromhex("3020300c06082a864886f70d020505000410"),
    "sha1": bytes.fromhex("3021300906052b0e03021a05000414"),
    "sha224": bytes.fromhex("302d300d06096086480165030402040500041c"),
    "sha256": bytes.fromhex("3031300d060960864801650304020105000420"),
    "sha384": bytes.fromhex("3041300d060960864801650304020205000430"),
    "sha512": bytes.fromhex("3051300d060960864801650304020305000440"),
}
_DIGEST_LENGTHS = {
    name: hashlib.new(name, usedforsecurity=False).digest_size for name in _HASH_NAMES
}
_SIGNATURE_MEMBER = re.compile(r"^META-INF/[^/]+\.(?:RSA|DSA|EC)$", re.IGNORECASE)
_TOKEN_PROPERTY = re.compile(r"^\s*xlet\.developerToken\s*[:=]\s*(.*)$")
_IDENTITY_PROPERTY = re.compile(
    r"^\s*(xlet\.(?:appId|vendor|mainClass|name))\s*[:=]\s*(.*)$"
)


def _require_crypto() -> None:
    if _CRYPTO_IMPORT_ERROR is not None:
        raise ProbeError("the cryptography dependency is required")


def _digest(name: str, data: bytes) -> bytes:
    try:
        return hashlib.new(name, data, usedforsecurity=False).digest()
    except (TypeError, ValueError) as error:
        raise ProbeError("unsupported digest algorithm") from error


def _logical_property_lines(text: str) -> tuple[str, ...]:
    logical: list[str] = []
    pending = ""
    for physical in text.splitlines():
        line = pending + (physical.lstrip() if pending else physical)
        trailing = len(line) - len(line.rstrip("\\"))
        if trailing % 2:
            pending = line[:-1]
            continue
        logical.append(line)
        pending = ""
    if pending:
        raise ProbeError("descriptor ends with an unterminated property continuation")
    return tuple(logical)


def _java_unescape(value: str) -> str:
    output: list[str] = []
    index = 0
    escapes = {"t": "\t", "n": "\n", "r": "\r", "f": "\f"}
    while index < len(value):
        character = value[index]
        if character != "\\":
            output.append(character)
            index += 1
            continue
        index += 1
        if index >= len(value):
            raise ProbeError("descriptor contains an invalid property escape")
        escaped = value[index]
        if escaped == "u":
            digits = value[index + 1 : index + 5]
            if len(digits) != 4 or not all(item in "0123456789abcdefABCDEF" for item in digits):
                raise ProbeError("descriptor contains an invalid Unicode escape")
            output.append(chr(int(digits, 16)))
            index += 5
            continue
        output.append(escapes.get(escaped, escaped))
        index += 1
    return "".join(output)


def parse_developer_token(descriptor: bytes) -> bytes:
    """Decode exactly one Java-properties developer token without echoing it."""

    try:
        text = descriptor.decode("latin-1")
    except UnicodeDecodeError as error:  # latin-1 is total, retained for defensive clarity
        raise ProbeError("descriptor text cannot be decoded") from error
    values: list[str] = []
    for line in _logical_property_lines(text):
        stripped = line.lstrip()
        if not stripped or stripped.startswith(("#", "!")):
            continue
        match = _TOKEN_PROPERTY.match(line)
        if match:
            values.append(_java_unescape(match.group(1).strip()))
    if len(values) != 1:
        raise ProbeError("descriptor must contain exactly one developer-token property")
    try:
        encoded = values[0].encode("ascii")
        token = base64.b64decode(encoded, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as error:
        raise ProbeError("developer-token property is not valid canonical Base64") from error
    if not token or base64.b64encode(token) != encoded:
        raise ProbeError("developer-token property is not valid canonical Base64")
    return token


def rsa_public_recover(signature: bytes, public_key: Any) -> RecoveryResult:
    """Perform the raw RSA public operation with explicit boundary classification."""

    _require_crypto()
    if not isinstance(public_key, rsa.RSAPublicKey):
        return RecoveryResult(status="non_rsa", modulus_bits=getattr(public_key, "key_size", 0))
    numbers = public_key.public_numbers()
    modulus_bits = public_key.key_size
    modulus_bytes = (modulus_bits + 7) // 8
    if len(signature) != modulus_bytes:
        return RecoveryResult(status="length_mismatch", modulus_bits=modulus_bits)
    signature_integer = int.from_bytes(signature, "big")
    if signature_integer >= numbers.n:
        return RecoveryResult(status="integer_ge_modulus", modulus_bits=modulus_bits)
    recovered = pow(signature_integer, numbers.e, numbers.n).to_bytes(modulus_bytes, "big")
    return RecoveryResult(
        status="recovered",
        modulus_bits=modulus_bits,
        encoded_message=recovered,
    )


def classify_pkcs1_v1_5(encoded_message: bytes | None) -> Pkcs1Classification:
    """Classify a raw RSA result as a PKCS#1 v1.5 encoded block."""

    if encoded_message is None or len(encoded_message) < 11:
        return Pkcs1Classification(valid=False)
    if encoded_message[0] != 0 or encoded_message[1] not in (1, 2):
        return Pkcs1Classification(valid=False)
    block_type = encoded_message[1]
    separator = encoded_message.find(b"\0", 2)
    if separator < 10:
        return Pkcs1Classification(valid=False)
    padding_bytes = encoded_message[2:separator]
    if block_type == 1 and any(value != 0xFF for value in padding_bytes):
        return Pkcs1Classification(valid=False)
    if block_type == 2 and any(value == 0 for value in padding_bytes):
        return Pkcs1Classification(valid=False)
    payload = encoded_message[separator + 1 :]
    for algorithm, prefix in _DIGEST_INFO_PREFIXES.items():
        digest_length = _DIGEST_LENGTHS[algorithm]
        if len(payload) == len(prefix) + digest_length and payload.startswith(prefix):
            return Pkcs1Classification(
                valid=True,
                block_type=block_type,
                padding_bytes=len(padding_bytes),
                payload_length=len(payload),
                digest_algorithm=algorithm,
                digest_length=digest_length,
                _digest=payload[len(prefix) :],
            )
    raw_digest_length = len(payload) if len(payload) in set(_DIGEST_LENGTHS.values()) else None
    return Pkcs1Classification(
        valid=True,
        block_type=block_type,
        padding_bytes=len(padding_bytes),
        payload_length=len(payload),
        raw_digest_length=raw_digest_length,
    )


def _mgf1(seed: bytes, output_length: int, algorithm: str) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < output_length:
        output.extend(_digest(algorithm, seed + counter.to_bytes(4, "big")))
        counter += 1
    return bytes(output[:output_length])


def classify_pss(
    encoded_message: bytes | None,
    modulus_bits: int,
    algorithm: str,
    mgf_algorithm: str | None = None,
) -> PssClassification:
    """Recognize a strict EMSA-PSS structure without exposing its salt or hash."""

    mgf_algorithm = algorithm if mgf_algorithm is None else mgf_algorithm
    if algorithm not in _PSS_HASH_NAMES or mgf_algorithm not in _PSS_MGF_HASH_NAMES:
        raise ProbeError("unsupported digest algorithm")
    invalid = PssClassification(
        valid=False,
        digest_algorithm=algorithm,
        mgf_algorithm=mgf_algorithm,
    )
    if encoded_message is None or modulus_bits <= 1:
        return invalid
    encoded_bits = modulus_bits - 1
    encoded_length = (encoded_bits + 7) // 8
    digest_length = _DIGEST_LENGTHS[algorithm]
    if (
        len(encoded_message) != encoded_length
        or encoded_length < digest_length + 2
        or encoded_message[-1] != 0xBC
    ):
        return invalid
    database_length = encoded_length - digest_length - 1
    masked_database = encoded_message[:database_length]
    encoded_hash = encoded_message[database_length : database_length + digest_length]
    unused_bits = 8 * encoded_length - encoded_bits
    if unused_bits and masked_database[0] >> (8 - unused_bits):
        return invalid
    mask = _mgf1(encoded_hash, database_length, mgf_algorithm)
    database = bytearray(left ^ right for left, right in zip(masked_database, mask))
    if unused_bits:
        database[0] &= 0xFF >> unused_bits
    delimiter = 0
    while delimiter < len(database) and database[delimiter] == 0:
        delimiter += 1
    if delimiter >= len(database) or database[delimiter] != 1:
        return invalid
    salt = bytes(database[delimiter + 1 :])
    return PssClassification(
        valid=True,
        digest_algorithm=algorithm,
        mgf_algorithm=mgf_algorithm,
        salt_length=len(salt),
        canonical_salt=len(salt) == digest_length,
        _encoded_hash=encoded_hash,
        _salt=salt,
    )


def _safe_source(source: str) -> str:
    normalized = source.replace("\\", "/")
    if not normalized or any(ord(character) < 0x20 for character in normalized):
        raise ProbeError("candidate source is not a safe relative path")
    if re.match(r"^[A-Za-z]:", normalized):
        raise ProbeError("candidate source is not a safe relative path")
    base, marker, member = normalized.partition("!/")
    if not marker:
        base, marker, member = normalized.partition("#")
    base_path = PurePosixPath(base)
    if base_path.is_absolute() or ".." in base_path.parts or not base_path.parts:
        raise ProbeError("candidate source is not a safe relative path")
    if marker:
        member_path = PurePosixPath(member)
        if member_path.is_absolute() or ".." in member_path.parts or not member_path.parts:
            raise ProbeError("candidate source member is not safe")
    return normalized


def _safe_display_text(value: str) -> str:
    """Escape controls and non-printing Unicode before emitting metadata."""

    output: list[str] = []
    for character in value:
        if character.isprintable() and character not in ("\u2028", "\u2029"):
            output.append(character)
            continue
        codepoint = ord(character)
        escape = "\\u" if codepoint <= 0xFFFF else "\\U"
        width = 4 if codepoint <= 0xFFFF else 8
        output.append(f"{escape}{codepoint:0{width}x}")
    return "".join(output)


def _key_metadata(public_key: Any) -> tuple[str, int]:
    _require_crypto()
    if isinstance(public_key, rsa.RSAPublicKey):
        return "rsa", public_key.key_size
    if isinstance(public_key, dsa.DSAPublicKey):
        return "dsa", public_key.key_size
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return "ec", public_key.key_size
    raise ProbeError("unsupported public-key type")


def _spki_bytes(public_key: Any) -> bytes:
    _require_crypto()
    try:
        return public_key.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except (TypeError, ValueError) as error:
        raise ProbeError("input is not a supported public key") from error


def make_candidate(
    public_key: Any,
    source: str,
    *,
    certificate: Any | None = None,
) -> CandidateKey:
    """Create a metadata-only candidate while retaining the public key in memory."""

    source = _safe_source(source)
    key_type, bits = _key_metadata(public_key)
    spki = _spki_bytes(public_key)
    certificate_fingerprints: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()
    if certificate is not None:
        if not isinstance(certificate, x509.Certificate):
            raise ProbeError("certificate input is not an X.509 certificate")
        if _spki_bytes(certificate.public_key()) != spki:
            raise ProbeError("certificate public key does not match candidate key")
        certificate_fingerprints = (
            certificate.fingerprint(hashes.SHA256()).hex(),
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            subjects = (_safe_display_text(certificate.subject.rfc4514_string()),)
    return CandidateKey(
        public_key=public_key,
        spki_sha256=hashlib.sha256(spki).hexdigest(),
        key_type=key_type,
        bits=bits,
        sources=(source,),
        certificate_sha256=certificate_fingerprints,
        subjects=subjects,
    )


def deduplicate_candidates(candidates: Iterable[CandidateKey]) -> tuple[CandidateKey, ...]:
    """Deduplicate public identities by SPKI fingerprint and merge metadata."""

    grouped: dict[str, list[CandidateKey]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.spki_sha256, []).append(candidate)
    output: list[CandidateKey] = []
    for fingerprint in sorted(grouped):
        group = grouped[fingerprint]
        first = group[0]
        if any((item.key_type, item.bits) != (first.key_type, first.bits) for item in group):
            raise ProbeError("conflicting metadata for one SPKI fingerprint")
        output.append(
            CandidateKey(
                public_key=first.public_key,
                spki_sha256=fingerprint,
                key_type=first.key_type,
                bits=first.bits,
                sources=tuple(sorted({source for item in group for source in item.sources})),
                certificate_sha256=tuple(
                    sorted({value for item in group for value in item.certificate_sha256})
                ),
                subjects=tuple(sorted({value for item in group for value in item.subjects})),
            )
        )
    return tuple(output)


def _relative_source(path: Path, root: Path) -> str:
    try:
        relative = path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError) as error:
        raise ProbeError("input path must exist inside the corpus root") from error
    return _safe_source(relative.as_posix())


def enumerate_jar_signer_certificates(
    jar_path: Path,
    corpus_root: Path,
) -> tuple[CandidateKey, ...]:
    """Read PKCS#7 certificate records from JAR signature-block members."""

    _require_crypto()
    source_base = _relative_source(jar_path, corpus_root)
    candidates: list[CandidateKey] = []
    try:
        with zipfile.ZipFile(jar_path) as archive:
            members = sorted(name for name in archive.namelist() if _SIGNATURE_MEMBER.match(name))
            for member in members:
                safe_member = _safe_source(f"{source_base}!/{member}")
                block = archive.read(member)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        certificates = pkcs7.load_der_pkcs7_certificates(block)
                except ValueError as error:
                    raise ProbeError("JAR signature block is not valid DER PKCS#7") from error
                if not certificates:
                    raise ProbeError("JAR signature block contains no certificates")
                for certificate in certificates:
                    candidates.append(
                        make_candidate(
                            certificate.public_key(),
                            safe_member,
                            certificate=certificate,
                        )
                    )
    except (OSError, zipfile.BadZipFile, KeyError) as error:
        raise ProbeError("JAR input is missing or structurally invalid") from error
    return deduplicate_candidates(candidates)


class _JksReader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def take(self, length: int) -> bytes:
        if length < 0 or self.offset + length > len(self.data):
            raise ProbeError("JKS input is truncated")
        result = self.data[self.offset : self.offset + length]
        self.offset += length
        return result

    def u16(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack(">I", self.take(4))[0]

    def utf(self) -> str:
        try:
            return self.take(self.u16()).decode("utf-8")
        except UnicodeDecodeError as error:
            raise ProbeError("JKS input contains invalid text metadata") from error


def enumerate_jks_certificates(store_path: Path, corpus_root: Path) -> tuple[CandidateKey, ...]:
    """Parse public certificates from a Java JKS v1/v2 store."""

    _require_crypto()
    source_base = _relative_source(store_path, corpus_root)
    try:
        data = store_path.read_bytes()
    except OSError as error:
        raise ProbeError("JKS input cannot be read") from error
    reader = _JksReader(data)
    if reader.u32() != 0xFEEDFEED:
        raise ProbeError("JKS input has an invalid magic value")
    version = reader.u32()
    if version not in (1, 2):
        raise ProbeError("JKS input has an unsupported version")
    entry_count = reader.u32()
    if entry_count > 10_000:
        raise ProbeError("JKS input declares too many entries")
    candidates: list[CandidateKey] = []

    def read_certificate(source: str) -> None:
        if version == 2:
            reader.utf()
        certificate_data = reader.take(reader.u32())
        try:
            certificate = x509.load_der_x509_certificate(certificate_data)
        except ValueError as error:
            raise ProbeError("JKS entry contains an invalid X.509 certificate") from error
        candidates.append(
            make_candidate(
                certificate.public_key(),
                source,
                certificate=certificate,
            )
        )

    for entry_index in range(entry_count):
        tag = reader.u32()
        reader.utf()  # Alias is intentionally not emitted; it may contain an absolute build path.
        reader.take(8)  # Java timestamp.
        if tag == 1:
            reader.take(reader.u32())  # Encrypted private-key bytes are skipped, never parsed.
            chain_count = reader.u32()
            if chain_count > 10_000:
                raise ProbeError("JKS private-key entry declares an invalid chain length")
            for chain_index in range(chain_count):
                read_certificate(
                    f"{source_base}#entry:{entry_index:04d}-chain:{chain_index:04d}"
                )
        elif tag == 2:
            read_certificate(f"{source_base}#entry:{entry_index:04d}")
        else:
            raise ProbeError("JKS input contains an unsupported entry type")
    if len(data) - reader.offset != 20:
        raise ProbeError("JKS input has an invalid integrity-trailer length")
    return deduplicate_candidates(candidates)


def _load_ssh1_rsa(data: bytes) -> Any | None:
    try:
        parts = data.decode("ascii").strip().split()
    except UnicodeDecodeError:
        return None
    if len(parts) < 3 or not all(part.isdigit() for part in parts[:3]):
        return None
    declared_bits, exponent, modulus = map(int, parts[:3])
    if declared_bits <= 0 or exponent <= 1 or modulus <= 1:
        raise ProbeError("SSH1 public-key input has invalid numeric fields")
    try:
        key = rsa.RSAPublicNumbers(exponent, modulus).public_key()
    except (TypeError, ValueError) as error:
        raise ProbeError("SSH1 public-key input has invalid numeric fields") from error
    if key.key_size != declared_bits:
        raise ProbeError("SSH1 public-key bit length does not match its modulus")
    return key


def _load_mincrypt_rsa(data: bytes) -> Any | None:
    if len(data) != 524 or struct.unpack_from("<I", data, 0)[0] != 64:
        return None
    n0_inverse = struct.unpack_from("<I", data, 4)[0]
    modulus = int.from_bytes(data[8:264], "little")
    rr = int.from_bytes(data[264:520], "little")
    exponent = struct.unpack_from("<I", data, 520)[0]
    if exponent not in (3, 65_537) or modulus.bit_length() != 2_048:
        raise ProbeError("mincrypt RSA public-key structure is invalid")
    if ((modulus & 0xFFFFFFFF) * n0_inverse) & 0xFFFFFFFF != 0xFFFFFFFF:
        raise ProbeError("mincrypt RSA public-key n0inv invariant failed")
    expected_rr = pow(2, 4_096, modulus)
    if rr != expected_rr:
        raise ProbeError("mincrypt RSA public-key RR invariant failed")
    return rsa.RSAPublicNumbers(exponent, modulus).public_key()


def enumerate_public_key_file(key_path: Path, corpus_root: Path) -> tuple[CandidateKey, ...]:
    """Load one standalone public key or certificate without accepting private keys."""

    _require_crypto()
    source = _relative_source(key_path, corpus_root)
    try:
        data = key_path.read_bytes()
    except OSError as error:
        raise ProbeError("public-key input cannot be read") from error
    if b"PRIVATE KEY" in data:
        raise ProbeError("private-key input is not accepted")
    certificate = None
    public_key = _load_mincrypt_rsa(data)
    if public_key is None:
        for loader in (x509.load_pem_x509_certificate, x509.load_der_x509_certificate):
            try:
                certificate = loader(data)
                public_key = certificate.public_key()
                break
            except ValueError:
                continue
    if public_key is None:
        for loader in (
            serialization.load_pem_public_key,
            serialization.load_der_public_key,
            serialization.load_ssh_public_key,
        ):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", CryptographyDeprecationWarning)
                    public_key = loader(data)
                break
            except (TypeError, ValueError, UnsupportedAlgorithm):
                continue
    if public_key is None:
        public_key = _load_ssh1_rsa(data)
    if public_key is None:
        raise ProbeError("public-key input has no supported public structure")
    return (make_candidate(public_key, source, certificate=certificate),)


def discover_candidates(corpus_root: Path) -> tuple[CandidateKey, ...]:
    """Discover signed-JAR, JKS, certificate, and public-key candidates."""

    _require_crypto()
    try:
        root = corpus_root.resolve(strict=True)
    except FileNotFoundError as error:
        raise ProbeError("corpus root does not exist") from error
    if not root.is_dir():
        raise ProbeError("corpus root is not a directory")
    candidates: list[CandidateKey] = []
    for jar_path in sorted(root.rglob("*.jar")):
        candidates.extend(enumerate_jar_signer_certificates(jar_path, root))
    stores = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and (path.name.lower() == "cacerts" or path.suffix.lower() in {".jks", ".keystore"})
    )
    for store_path in stores:
        candidates.extend(enumerate_jks_certificates(store_path, root))
    public_suffixes = {".pub", ".pem", ".crt", ".cer", ".cert", ".der", ".0"}
    public_files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path not in stores
        and path.suffix.lower() in public_suffixes
    )
    for public_path in public_files:
        candidates.extend(enumerate_public_key_file(public_path, root))
    result = deduplicate_candidates(candidates)
    if not result:
        raise ProbeError("corpus contains no supported candidate public keys")
    return result


def _add_message(messages: dict[str, bytes], value: bytes) -> None:
    messages.setdefault(hashlib.sha256(value).hexdigest(), value)


def _descriptor_messages(descriptor_paths: Sequence[Path]) -> tuple[bytes, ...]:
    messages: dict[str, bytes] = {}
    for descriptor_path in descriptor_paths:
        try:
            descriptor = descriptor_path.read_bytes()
        except OSError as error:
            raise ProbeError("token descriptor cannot be read") from error
        _add_message(messages, descriptor)
        _add_message(messages, descriptor.replace(b"\r\n", b"\n"))
        without_token = b"\n".join(
            line
            for line in descriptor.replace(b"\r\n", b"\n").split(b"\n")
            if not line.lstrip().startswith(b"xlet.developerToken")
        )
        _add_message(messages, without_token)
        text = descriptor.decode("latin-1")
        identity_values: list[bytes] = []
        for line in _logical_property_lines(text):
            match = _IDENTITY_PROPERTY.match(line)
            if match:
                value = _java_unescape(match.group(2).strip()).encode("utf-8")
                identity_values.append(value)
                _add_message(messages, value)
        if len(identity_values) >= 3:
            for delimiter in (b"", b"|", b":", b"\n"):
                _add_message(messages, delimiter.join(identity_values[:3]))
        sibling = descriptor_path.parent / "jars" / "key.jar"
        if sibling.is_file():
            try:
                with zipfile.ZipFile(sibling) as archive:
                    signed_descriptor = archive.read("xlet.properties")
            except (OSError, zipfile.BadZipFile, KeyError) as error:
                raise ProbeError("sibling key JAR has no valid signed descriptor") from error
            _add_message(messages, signed_descriptor)
            _add_message(messages, signed_descriptor.replace(b"\r\n", b"\n"))
    initial = tuple(messages.values())
    for message in initial:
        for algorithm in ("sha1", "sha256", "sha384", "sha512"):
            digest = _digest(algorithm, message)
            _add_message(messages, digest)
            _add_message(messages, digest.hex().encode("ascii"))
    return tuple(messages[key] for key in sorted(messages))


def _candidate_digest_messages(candidates: Sequence[CandidateKey]) -> tuple[bytes, ...]:
    messages: dict[str, bytes] = {}
    for candidate in candidates:
        for fingerprint in (candidate.spki_sha256, *candidate.certificate_sha256):
            raw = bytes.fromhex(fingerprint)
            _add_message(messages, raw)
            _add_message(messages, fingerprint.encode("ascii"))
    return tuple(messages[key] for key in sorted(messages))


def _pkcs1_matches(
    classification: Pkcs1Classification,
    message: bytes,
    algorithm: str,
) -> bool:
    return (
        classification.valid
        and classification.block_type == 1
        and classification.digest_algorithm == algorithm
        and classification._digest is not None
        and classification._digest == _digest(algorithm, message)
    )


def _pss_matches(classification: PssClassification, message: bytes) -> bool:
    if (
        not classification.valid
        or classification._encoded_hash is None
        or classification._salt is None
    ):
        return False
    message_hash = _digest(classification.digest_algorithm, message)
    expected = _digest(
        classification.digest_algorithm,
        b"\0" * 8 + message_hash + classification._salt,
    )
    return expected == classification._encoded_hash


def build_summary(
    token: bytes,
    candidates: Iterable[CandidateKey],
    messages: Sequence[bytes] = (),
) -> dict[str, Any]:
    """Build a deterministic metadata-only summary of RSA recovery attempts."""

    if not isinstance(token, bytes) or not token:
        raise ProbeError("token input must be nonempty bytes")
    unique_candidates = deduplicate_candidates(candidates)
    if any(not isinstance(message, bytes) for message in messages):
        raise ProbeError("verification messages must be bytes")
    unique_messages = {
        hashlib.sha256(message).hexdigest(): bytes(message)
        for message in messages
    }
    variants = (
        ("as_stored", token),
        ("whole_byte_reversed", token[::-1]),
    )
    recovery_counts = {
        "cases": 0,
        "length_compatible": 0,
        "recovered": 0,
        "integer_ge_modulus": 0,
        "length_mismatch": 0,
        "non_rsa": 0,
    }
    valid_pkcs1: list[dict[str, Any]] = []
    valid_pss: list[dict[str, Any]] = []
    match_count = 0
    match_metadata: set[tuple[str, str, str, str, str]] = set()
    verification_attempts = 0

    for candidate in unique_candidates:
        for variant_name, variant in variants:
            recovery_counts["cases"] += 1
            recovery = rsa_public_recover(variant, candidate.public_key)
            if recovery.status == "non_rsa":
                recovery_counts["non_rsa"] += 1
                continue
            if recovery.status == "length_mismatch":
                recovery_counts["length_mismatch"] += 1
                continue
            recovery_counts["length_compatible"] += 1
            if recovery.status == "integer_ge_modulus":
                recovery_counts["integer_ge_modulus"] += 1
            elif recovery.status == "recovered":
                recovery_counts["recovered"] += 1

            pkcs1 = classify_pkcs1_v1_5(recovery.encoded_message)
            if pkcs1.valid:
                valid_pkcs1.append(
                    {
                        "spki_sha256": candidate.spki_sha256,
                        "variant": variant_name,
                        "block_type": pkcs1.block_type,
                        "padding_bytes": pkcs1.padding_bytes,
                        "payload_length": pkcs1.payload_length,
                        "digest_algorithm": pkcs1.digest_algorithm,
                        "digest_length": pkcs1.digest_length,
                        "raw_digest_length": pkcs1.raw_digest_length,
                    }
                )
            pss_results = {
                (algorithm, mgf_algorithm): classify_pss(
                    recovery.encoded_message,
                    candidate.bits,
                    algorithm,
                    mgf_algorithm,
                )
                for algorithm in _PSS_HASH_NAMES
                for mgf_algorithm in _PSS_MGF_HASH_NAMES
            }
            for classification in pss_results.values():
                if classification.valid:
                    valid_pss.append(
                        {
                            "spki_sha256": candidate.spki_sha256,
                            "variant": variant_name,
                            "digest_algorithm": classification.digest_algorithm,
                            "mgf_algorithm": classification.mgf_algorithm,
                            "salt_length": classification.salt_length,
                            "canonical_salt": classification.canonical_salt,
                        }
                    )
            for message in unique_messages.values():
                for algorithm in _HASH_NAMES:
                    verification_attempts += 1
                    if _pkcs1_matches(pkcs1, message, algorithm):
                        match_count += 1
                        match_metadata.add(
                            (
                                candidate.spki_sha256,
                                variant_name,
                                "pkcs1_v1_5",
                                algorithm,
                                "",
                            )
                        )
                for (algorithm, mgf_algorithm), pss in pss_results.items():
                    verification_attempts += 1
                    if _pss_matches(pss, message):
                        match_count += 1
                        match_metadata.add(
                            (
                                candidate.spki_sha256,
                                variant_name,
                                "pss",
                                algorithm,
                                mgf_algorithm,
                            )
                        )

    candidate_items = [
        {
            "spki_sha256": candidate.spki_sha256,
            "key_type": candidate.key_type,
            "bits": candidate.bits,
            "sources": list(candidate.sources),
            "certificate_sha256": list(candidate.certificate_sha256),
            "subjects": list(candidate.subjects),
        }
        for candidate in unique_candidates
    ]
    return {
        "token": {
            "byte_length": len(token),
            "sha256": hashlib.sha256(token).hexdigest(),
        },
        "candidates": {
            "distinct_keys": len(unique_candidates),
            "rsa": sum(item.key_type == "rsa" for item in unique_candidates),
            "rsa_length_compatible": sum(
                item.key_type == "rsa" and (item.bits + 7) // 8 == len(token)
                for item in unique_candidates
            ),
            "non_rsa": sum(item.key_type != "rsa" for item in unique_candidates),
            "items": candidate_items,
        },
        "recovery": recovery_counts,
        "pkcs1_v1_5": {
            "valid_blocks": len(valid_pkcs1),
            "classified": sorted(
                valid_pkcs1,
                key=lambda item: (item["spki_sha256"], item["variant"]),
            ),
        },
        "pss": {
            "valid_structures": len(valid_pss),
            "classified": sorted(
                valid_pss,
                key=lambda item: (
                    item["spki_sha256"],
                    item["variant"],
                    item["digest_algorithm"],
                    item["mgf_algorithm"],
                ),
            ),
        },
        "verification": {
            "message_count": len(unique_messages),
            "attempts": verification_attempts,
            "matches": match_count,
            "matched_algorithms": [
                {
                    "spki_sha256": fingerprint,
                    "variant": variant,
                    "scheme": scheme,
                    "digest_algorithm": algorithm,
                    **({"mgf_algorithm": mgf_algorithm} if mgf_algorithm else {}),
                }
                for fingerprint, variant, scheme, algorithm, mgf_algorithm in sorted(
                    match_metadata
                )
            ],
        },
    }


def render_summary(summary: dict[str, Any], output_format: str) -> str:
    """Render only the sanitized fields created by :func:`build_summary`."""

    if output_format == "json":
        return json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if output_format != "text":
        raise ProbeError("output format must be json or text")
    token = summary["token"]
    candidates = summary["candidates"]
    recovery = summary["recovery"]
    verification = summary["verification"]
    lines = [
        f"token.byte_length={token['byte_length']}",
        f"token.sha256={token['sha256']}",
        f"candidates.distinct_keys={candidates['distinct_keys']}",
        f"candidates.rsa={candidates['rsa']}",
        f"candidates.rsa_length_compatible={candidates['rsa_length_compatible']}",
        f"candidates.non_rsa={candidates['non_rsa']}",
    ]
    for candidate in candidates["items"]:
        lines.append(
            "candidate="
            f"{candidate['spki_sha256']} {candidate['key_type']} {candidate['bits']}"
        )
        lines.extend(f"  source={source}" for source in candidate["sources"])
        lines.extend(
            f"  certificate_sha256={fingerprint}"
            for fingerprint in candidate["certificate_sha256"]
        )
        lines.extend(f"  subject={subject}" for subject in candidate["subjects"])
    lines.extend(
        (
            f"recovery.cases={recovery['cases']}",
            f"recovery.length_compatible={recovery['length_compatible']}",
            f"recovery.recovered={recovery['recovered']}",
            f"recovery.integer_ge_modulus={recovery['integer_ge_modulus']}",
            f"recovery.length_mismatch={recovery['length_mismatch']}",
            f"recovery.non_rsa={recovery['non_rsa']}",
            f"pkcs1_v1_5.valid_blocks={summary['pkcs1_v1_5']['valid_blocks']}",
            f"pss.valid_structures={summary['pss']['valid_structures']}",
            f"verification.message_count={verification['message_count']}",
            f"verification.attempts={verification['attempts']}",
            f"verification.matches={verification['matches']}",
        )
    )
    return "\n".join(lines) + "\n"


def probe_corpus(
    corpus_root: Path,
    descriptor_inputs: Sequence[Path],
) -> dict[str, Any]:
    """Read the requested corpus and return a sanitized deterministic summary."""

    _require_crypto()
    try:
        root = corpus_root.resolve(strict=True)
    except FileNotFoundError as error:
        raise ProbeError("corpus root does not exist") from error
    if not descriptor_inputs:
        raise ProbeError("at least one token descriptor is required")
    descriptors: list[Path] = []
    tokens: list[bytes] = []
    for descriptor_input in descriptor_inputs:
        candidate = descriptor_input if descriptor_input.is_absolute() else root / descriptor_input
        try:
            descriptor = candidate.resolve(strict=True)
            descriptor.relative_to(root)
            descriptor_bytes = descriptor.read_bytes()
        except (FileNotFoundError, OSError, ValueError) as error:
            raise ProbeError("token descriptor must exist inside the corpus root") from error
        descriptors.append(descriptor)
        tokens.append(parse_developer_token(descriptor_bytes))
    if any(token != tokens[0] for token in tokens[1:]):
        raise ProbeError("token descriptors do not contain one identical decoded value")
    candidates = discover_candidates(root)
    messages = list(_descriptor_messages(descriptors))
    messages.extend(_candidate_digest_messages(candidates))
    return build_summary(tokens[0], candidates, messages)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify an opaque developer token against public keys in a corpus"
    )
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument(
        "--token-descriptor",
        required=True,
        action="append",
        type=Path,
        help="descriptor path relative to the corpus root; repeat for replicas",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        summary = probe_corpus(args.corpus_root, args.token_descriptor)
        rendered = render_summary(summary, args.format)
    except ProbeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
