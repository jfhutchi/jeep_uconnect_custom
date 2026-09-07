"""Read-only structural inspection for recovered RA4 resident packages.

The tool recognizes both the factory installed-layout form and the live
single-JAR member-routing contract recovered from the AMS Installer class. It
can test whether an installed payload/key pair is a consistent image of that
split, but it never reconstructs an archive, signs, asserts private authority,
or produces an install request.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable
import zipfile


class PackageInspectionError(ValueError):
    """Raised when an input cannot be inspected safely and completely."""


_MAX_MEMBER_SIZE = 64 * 1024 * 1024
_MAX_TOTAL_SIZE = 512 * 1024 * 1024
_SIGNATURE_FILE = re.compile(r"^META-INF/([^/]+)\.SF$", re.IGNORECASE)
_SIGNATURE_BLOCK = re.compile(r"^META-INF/([^/]+)\.(RSA|DSA|EC)$", re.IGNORECASE)
_AMS_SIGNATURE_FILE = re.compile(r"^META-INF/([^/]+)\.SF$")
_AMS_SIGNATURE_BLOCK = re.compile(r"^META-INF/([^/]+)\.(RSA|DSA)$")
_AMS_KEY_SUFFIXES = (".MF", ".RSA", ".SF", ".DSA")
_AMS_APP_ID_CHARACTERS = frozenset(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-"
)
_CORE_IDENTITY_KEYS = (
    "xlet.appId",
    "xlet.mainClass",
    "xlet.name",
    "xlet.vendor",
    "xlet.policy",
    "xlet.policy.default",
    "xlet.developerToken",
    "xlet.deviceToken",
)
_SAFETY_DESCRIPTOR_KEYS = (
    "xlet.AppCategory",
    "xlet.PauseAllowed",
    "xlet.autostart",
    "xlet.daemon",
    "xlet.hasGUI",
    "xlet.headless",
    "xlet.isAudio",
    "xlet.writeEnabled",
)
_PROTECTED_DESCRIPTOR_KEYS = _CORE_IDENTITY_KEYS + _SAFETY_DESCRIPTOR_KEYS
_TRUE = frozenset(("true", "yes", "1"))
_TOKEN_KEYS = frozenset(("xlet.developerToken", "xlet.deviceToken"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _content_set_sha256(members: dict[str, bytes]) -> str:
    inventory = [
        {"name": name, "sha256": _sha256(members[name]), "size": len(members[name])}
        for name in sorted(members)
    ]
    canonical = json.dumps(inventory, separators=(",", ":"), sort_keys=True).encode("ascii")
    return _sha256(canonical)


def _ams_routes_to_key(name: str) -> bool:
    """Mirror Installer.copyAndCheck's exact, case-sensitive suffix tests."""

    return name.endswith(_AMS_KEY_SUFFIXES)


def _ams_app_id_valid(value: str | None) -> bool:
    return bool(value) and all(character in _AMS_APP_ID_CHARACTERS for character in value)


def _single_jar_transformation_report(members: dict[str, bytes]) -> dict[str, Any]:
    payload_names = sorted(name for name in members if not _ams_routes_to_key(name))
    key_names = sorted(
        name
        for name in members
        if _ams_routes_to_key(name) or name == "xlet.properties"
    )
    overlap = sorted(set(payload_names) & set(key_names))
    return {
        "archive_byte_identity_recoverable": False,
        "content_set_sha256": _content_set_sha256(members),
        "key_member_names": key_names,
        "overlap_member_names": overlap,
        "payload_member_names": payload_names,
        "predicted_incoming_member_count": len(members),
        "routing_rule": {
            "case_sensitive": True,
            "duplicate_to_both": ["xlet.properties"],
            "key_suffixes": list(_AMS_KEY_SUFFIXES),
            "otherwise": "payload JAR only",
        },
    }


def _inverse_transformation_report(
    payload_members: dict[str, bytes], key_members: dict[str, bytes]
) -> dict[str, Any]:
    errors: list[str] = []
    payload_names = set(payload_members)
    key_names = set(key_members)
    misplaced_payload = sorted(name for name in payload_names if _ams_routes_to_key(name))
    misplaced_key = sorted(
        name
        for name in key_names
        if not _ams_routes_to_key(name) and name != "xlet.properties"
    )
    overlap = sorted(payload_names & key_names)
    if misplaced_payload:
        errors.append("payload JAR contains members AMS routes only to key.jar")
    if misplaced_key:
        errors.append("key.jar contains members AMS routes only to the payload JAR")
    if overlap != ["xlet.properties"]:
        errors.append("payload/key overlap is not exactly root xlet.properties")
    elif payload_members["xlet.properties"] != key_members["xlet.properties"]:
        errors.append("payload/key xlet.properties copies differ")

    reconstructed = dict(payload_members)
    conflicts: list[str] = []
    for name, data in key_members.items():
        if name in reconstructed and reconstructed[name] != data:
            conflicts.append(name)
        else:
            reconstructed[name] = data
    if conflicts:
        errors.append("payload/key member bytes conflict")

    report = _single_jar_transformation_report(reconstructed)
    report.update(
        {
            "consistent_with_ams_split": not errors,
            "errors": errors,
            "misplaced_key_member_names": misplaced_key,
            "misplaced_payload_member_names": misplaced_payload,
            "overlap_member_names": overlap,
        }
    )
    if conflicts:
        report["content_set_sha256"] = None
        report["conflicting_member_names"] = sorted(conflicts)
    return report


def is_safe_leaf_name(value: str) -> bool:
    """Return whether a descriptor value is one filesystem leaf on Windows/QNX."""

    return bool(
        value
        and value not in (".", "..")
        and not any(character in value for character in ("/", "\\", ":", "\x00"))
        and PurePosixPath(value).name == value
    )


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
            output.append("\\")
            break
        escaped = value[index]
        if escaped == "u":
            digits = value[index + 1 : index + 5]
            if len(digits) != 4 or not all(
                item in "0123456789abcdefABCDEF" for item in digits
            ):
                raise PackageInspectionError("descriptor has an invalid Unicode escape")
            output.append(chr(int(digits, 16)))
            index += 5
            continue
        output.append(escapes.get(escaped, escaped))
        index += 1
    return "".join(output)


def parse_java_properties(data: bytes) -> dict[str, str]:
    """Parse the Java-properties subset observed in recovered descriptors."""

    text = data.decode("latin-1")
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
        raise PackageInspectionError("descriptor has an unterminated continuation")

    properties: dict[str, str] = {}
    for line in logical:
        stripped = line.lstrip()
        if not stripped or stripped.startswith(("#", "!")):
            continue
        escaped = False
        separator = None
        for index, character in enumerate(line):
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character in "=:" or character.isspace():
                separator = index
                break
        if separator is None:
            raw_key, raw_value = line, ""
        else:
            raw_key = line[:separator]
            value_start = separator
            while value_start < len(line) and line[value_start].isspace():
                value_start += 1
            if value_start < len(line) and line[value_start] in "=:":
                value_start += 1
            while value_start < len(line) and line[value_start].isspace():
                value_start += 1
            raw_value = line[value_start:]
        key = _java_unescape(raw_key)
        if not key:
            raise PackageInspectionError("descriptor has an empty property key")
        # java.util.Properties.load keeps the last occurrence of a duplicate key.
        properties[key] = _java_unescape(raw_value)
    return properties


def _safe_member_name(name: str) -> str:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise PackageInspectionError("ZIP contains an unsafe member name")
    return str(path)


def _read_zip(path: Path) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    try:
        archive = zipfile.ZipFile(path, "r")
    except (OSError, zipfile.BadZipFile) as error:
        raise PackageInspectionError("input is not a readable ZIP/JAR") from error
    with archive:
        infos = archive.infolist()
        names = [_safe_member_name(info.filename.rstrip("/")) for info in infos if not info.is_dir()]
        if len(names) != len(set(names)):
            raise PackageInspectionError("ZIP/JAR has duplicate members")
        total = sum(info.file_size for info in infos)
        if total > _MAX_TOTAL_SIZE:
            raise PackageInspectionError("ZIP/JAR exceeds the total expansion limit")
        members: dict[str, bytes] = {}
        inventory: list[dict[str, Any]] = []
        for info in infos:
            if info.is_dir():
                continue
            name = _safe_member_name(info.filename)
            if info.file_size > _MAX_MEMBER_SIZE:
                raise PackageInspectionError("ZIP/JAR member exceeds the expansion limit")
            try:
                data = archive.read(info)
            except (OSError, RuntimeError, zipfile.BadZipFile) as error:
                raise PackageInspectionError("ZIP/JAR member cannot be read") from error
            if len(data) != info.file_size:
                raise PackageInspectionError("ZIP/JAR member size is inconsistent")
            members[name] = data
            inventory.append(
                {
                    "name": name,
                    "sha256": _sha256(data),
                    "size": len(data),
                }
            )
        inventory.sort(key=lambda item: item["name"])
        return members, inventory


def _inventory_from_members(members: dict[str, bytes]) -> list[dict[str, Any]]:
    return [
        {"name": name, "sha256": _sha256(members[name]), "size": len(members[name])}
        for name in sorted(members)
    ]


def _unfold_manifest(data: bytes) -> list[list[tuple[str, str]]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    physical = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    logical: list[str] = []
    for line in physical:
        if line.startswith(" "):
            if not logical:
                raise PackageInspectionError("JAR manifest begins with a continuation")
            logical[-1] += line[1:]
        else:
            logical.append(line)
    sections: list[list[tuple[str, str]]] = [[]]
    for line in logical:
        if not line:
            if sections[-1]:
                sections.append([])
            continue
        if ": " not in line:
            raise PackageInspectionError("JAR manifest has a malformed attribute")
        key, value = line.split(": ", 1)
        if any(existing.lower() == key.lower() for existing, _ in sections[-1]):
            raise PackageInspectionError("JAR manifest section has a duplicate attribute")
        sections[-1].append((key, value))
    return [section for section in sections if section]


def _section_map(section: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {key.lower(): value for key, value in section}


def _decode_digest(value: str) -> bytes | None:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError):
        return None


def _digest_matches(algorithm: str, expected: str, data: bytes) -> bool:
    normalized = algorithm.lower().replace("-", "")
    if normalized not in ("sha1", "sha256"):
        return False
    decoded = _decode_digest(expected)
    return decoded is not None and decoded == hashlib.new(normalized, data).digest()


def _certificate_metadata(blocks: dict[str, bytes]) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.serialization import pkcs7
    except ImportError:
        return [], ["cryptography dependency unavailable"] if blocks else []

    certificates: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for name in sorted(blocks):
        try:
            parsed = pkcs7.load_der_pkcs7_certificates(blocks[name])
        except Exception:
            errors.append("%s: PKCS#7 certificates could not be parsed" % name)
            continue
        if not parsed:
            errors.append("%s: PKCS#7 block contains no certificates" % name)
            continue
        for certificate in parsed:
            der = certificate.public_bytes(serialization.Encoding.DER)
            fingerprint = _sha256(der)
            if hasattr(certificate, "not_valid_before_utc"):
                not_before = certificate.not_valid_before_utc
                not_after = certificate.not_valid_after_utc
            else:  # pragma: no cover - legacy cryptography compatibility
                not_before = certificate.not_valid_before
                not_after = certificate.not_valid_after
            certificates[fingerprint] = {
                "certificate_sha256": fingerprint,
                "issuer": certificate.issuer.rfc4514_string(),
                "not_valid_after": not_after.isoformat(),
                "not_valid_before": not_before.isoformat(),
                "serial_number_hex": format(certificate.serial_number, "x"),
                "subject": certificate.subject.rfc4514_string(),
            }
    return [certificates[key] for key in sorted(certificates)], errors


def _identity_report(installed: dict[str, str], signed: dict[str, str] | None) -> dict[str, Any]:
    if signed is None:
        return {
            "allowed_descriptor_differences": [],
            "core_keys_checked": list(_CORE_IDENTITY_KEYS),
            "protected_keys_checked": list(_PROTECTED_DESCRIPTOR_KEYS),
            "signed_descriptor_present": False,
            "signed_installed_core_match": False,
            "signed_installed_protected_match": False,
        }
    differences = sorted(
        key for key in set(installed) | set(signed) if installed.get(key) != signed.get(key)
    )
    core_match = all(
        installed.get(key) == signed.get(key)
        for key in _CORE_IDENTITY_KEYS
        if key in installed or key in signed
    )
    protected_match = all(
        installed.get(key) == signed.get(key)
        for key in _PROTECTED_DESCRIPTOR_KEYS
        if key in installed or key in signed
    )
    allowed = [key for key in differences if key == "xlet.jarFile"]
    return {
        "allowed_descriptor_differences": allowed,
        "core_keys_checked": list(_CORE_IDENTITY_KEYS),
        "protected_keys_checked": list(_PROTECTED_DESCRIPTOR_KEYS),
        "signed_descriptor_present": True,
        "signed_installed_core_match": core_match,
        "signed_installed_protected_match": protected_match,
    }


def _hello_profile(
    installed: dict[str, str], signed: dict[str, str] | None = None
) -> dict[str, Any]:
    prohibited: list[str] = []
    for properties in (installed, signed or {}):
        for key in ("xlet.autostart", "xlet.daemon", "xlet.isAudio", "xlet.writeEnabled"):
            if properties.get(key, "false").strip().lower() in _TRUE:
                prohibited.append("%s=true" % key)
        for key in sorted(_TOKEN_KEYS):
            if key in properties:
                prohibited.append("%s=<present>" % key)
        for key in sorted(properties):
            lowered = key.lower()
            if any(marker in lowered for marker in ("appmgrpermission", "projectionpermission", "vehicleservicepermission")):
                prohibited.append("%s=<present>" % key)
    prohibited = sorted(set(prohibited))
    return {
        "prohibited_declarations": prohibited,
        "safe": not prohibited,
    }


def _entitlement_report(properties: dict[str, str]) -> dict[str, Any]:
    return {
        "app_category": properties.get("xlet.AppCategory"),
        "audio": properties.get("xlet.isAudio", "false").lower() in _TRUE,
        "autostart": properties.get("xlet.autostart", "false").lower() in _TRUE,
        "daemon": properties.get("xlet.daemon", "false").lower() in _TRUE,
        "developer_token_present": "xlet.developerToken" in properties,
        "device_token_present": "xlet.deviceToken" in properties,
        "policy": properties.get("xlet.policy"),
        "policy_default": properties.get("xlet.policy.default"),
        "write_enabled": properties.get("xlet.writeEnabled", "false").lower() in _TRUE,
    }


def _base_installability() -> list[str]:
    return [
        "authorized issuer-produced incoming JAR and authentication material",
        "authorized application ID issuance",
        "legitimate signer or developer-token issuance",
        "AMS signer-to-principal and policy construction",
        "effective DRM/launcher grant for the new identity",
        "authorized installer transport and uninstall procedure",
        "bench target lifecycle and foreground acceptance",
    ]


def _inspect_key_members(
    key_members: dict[str, bytes],
    key_inventory: list[dict[str, Any]],
    payload_members: dict[str, bytes],
) -> tuple[dict[str, Any], list[str], dict[str, str] | None, dict[str, bytes]]:
    errors: list[str] = []
    manifest = key_members.get("META-INF/MANIFEST.MF")
    signed_descriptor_data = key_members.get("xlet.properties")
    signed_properties = parse_java_properties(signed_descriptor_data) if signed_descriptor_data is not None else None
    signature_files = sorted(name for name in key_members if _SIGNATURE_FILE.match(name))
    signature_blocks = sorted(name for name in key_members if _SIGNATURE_BLOCK.match(name))
    signature_stems = {(_SIGNATURE_FILE.match(name).group(1).lower()) for name in signature_files}
    block_stems = {(_SIGNATURE_BLOCK.match(name).group(1).lower()) for name in signature_blocks}
    if manifest is None:
        errors.append("key.jar META-INF/MANIFEST.MF")
    if signed_descriptor_data is None:
        errors.append("key.jar signed xlet.properties")
    if not signature_stems or signature_stems != block_stems:
        errors.append("key.jar JAR-signature metadata")

    covered_payload: set[str] = set()
    same_name_mismatches: list[str] = []
    digest_mismatches = 0
    missing_named: list[str] = []
    digest_records = 0
    manifest_digest_matches = False
    signed_descriptor_covered = False
    if manifest is not None:
        sections = _unfold_manifest(manifest)
        manifest_main = _section_map(sections[0]) if sections else {}
        if not manifest_main.get("manifest-version"):
            errors.append("key.jar manifest version")
        named: list[dict[str, str]] = []
        for section in sections[1:]:
            mapped = _section_map(section)
            if "name" in mapped:
                named.append(mapped)
        for section in named:
            name = _safe_member_name(section["name"])
            source_from_key = name in key_members
            if source_from_key and name in payload_members:
                if key_members[name] != payload_members[name]:
                    same_name_mismatches.append(name)
                else:
                    covered_payload.add(name)
            elif name in payload_members:
                covered_payload.add(name)
            source = key_members.get(name)
            if source is None:
                source = payload_members.get(name)
            if source is None:
                missing_named.append(name)
                continue
            digests = [
                (key[: -len("-digest")], value)
                for key, value in section.items()
                if key.endswith("-digest")
            ]
            if not digests:
                digest_mismatches += 1
                continue
            section_matches: list[bool] = []
            for algorithm, expected in digests:
                digest_records += 1
                matches = _digest_matches(algorithm, expected, source)
                section_matches.append(matches)
                if not matches:
                    digest_mismatches += 1
            if name == "xlet.properties" and source_from_key and all(section_matches):
                signed_descriptor_covered = True

        sf_results: list[bool] = []
        sf_versions_valid = True
        for name in signature_files:
            sf_sections = _unfold_manifest(key_members[name])
            sf_main = _section_map(sf_sections[0]) if sf_sections else {}
            if not sf_main.get("signature-version"):
                sf_versions_valid = False
            file_results: list[bool] = []
            for key, value in sf_main.items():
                suffix = "-digest-manifest"
                if key.endswith(suffix):
                    file_results.append(
                        _digest_matches(key[: -len(suffix)], value, manifest)
                    )
            sf_results.append(bool(file_results) and all(file_results))
        manifest_digest_matches = (
            sf_versions_valid and bool(sf_results) and all(sf_results)
        )
        if not sf_versions_valid:
            errors.append("key.jar .SF signature version")
        if not manifest_digest_matches:
            errors.append("key.jar .SF manifest digest")

    if signed_descriptor_data is not None and not signed_descriptor_covered:
        errors.append("signed xlet.properties manifest coverage")

    uncovered = sorted(set(payload_members) - covered_payload)
    if uncovered:
        errors.append("detached manifest payload coverage")
    if missing_named:
        errors.append("detached manifest named members")
    if digest_mismatches:
        errors.append("detached manifest digest match")
    if same_name_mismatches:
        errors.append("detached manifest same-name member mismatch")

    blocks = {name: key_members[name] for name in signature_blocks}
    certificates, certificate_errors = _certificate_metadata(blocks)
    if certificate_errors:
        errors.append("key.jar PKCS#7 certificate metadata")
    report = {
        "certificate_parse_errors": certificate_errors,
        "certificates": certificates,
        "digest_mismatches": digest_mismatches,
        "digest_records_checked": digest_records,
        "key_jar_inventory": key_inventory,
        "manifest_digest_matches": manifest_digest_matches,
        "missing_named_members": sorted(missing_named),
        "payload_members_covered": len(covered_payload),
        "same_name_member_mismatches": sorted(same_name_mismatches),
        "signature_blocks": signature_blocks,
        "signature_files": signature_files,
        "signature_math_verified": False,
        "signed_descriptor_covered": signed_descriptor_covered,
        "uncovered_payload_members": uncovered,
    }
    return report, errors, signed_properties, key_members


def _inspect_directory(root: Path, hello_profile: bool) -> dict[str, Any]:
    prog = root / "prog"
    jars = prog / "jars"
    descriptor_path = prog / "xlet.properties"
    errors: list[str] = []
    if not descriptor_path.is_file():
        raise PackageInspectionError("installed layout has no prog/xlet.properties")
    installed_data = descriptor_path.read_bytes()
    installed = parse_java_properties(installed_data)
    required = ("xlet.appId", "xlet.jarFile", "xlet.mainClass", "xlet.name", "xlet.version")
    for key in required:
        if not installed.get(key):
            errors.append("installed descriptor missing %s" % key)
    app_id = installed.get("xlet.appId")
    jar_file = installed.get("xlet.jarFile")
    if app_id and not _ams_app_id_valid(app_id):
        errors.append("xlet.appId uses characters rejected by AMS")
    if app_id and not is_safe_leaf_name(app_id):
        errors.append("xlet.appId is not a safe directory leaf")
    if app_id and root.name != app_id:
        errors.append("directory name does not match xlet.appId")

    jar_file_safe = bool(jar_file and is_safe_leaf_name(jar_file))
    if jar_file and not jar_file_safe:
        errors.append("unsafe installed xlet.jarFile")
    payload_path = jars / jar_file if jar_file_safe else None
    payload_members: dict[str, bytes] = {}
    payload_inventory: list[dict[str, Any]] = []
    payload_sha = None
    payload_size = None
    payload_descriptor_data: bytes | None = None
    if payload_path is None or not payload_path.is_file():
        errors.append("descriptor-selected executable JAR")
    else:
        payload_members, payload_inventory = _read_zip(payload_path)
        payload_descriptor_data = payload_members.get("xlet.properties")
        if payload_descriptor_data is None:
            errors.append("executable JAR root xlet.properties")
        payload_bytes = payload_path.read_bytes()
        payload_sha = _sha256(payload_bytes)
        payload_size = len(payload_bytes)

    key_path = jars / "key.jar"
    magic_path = jars / "magic.txt"
    if not magic_path.is_file() or magic_path.read_bytes() != b"HB_CMC":
        errors.append("prog/jars/magic.txt HB_CMC marker")
    authentication: dict[str, Any]
    signed_properties: dict[str, str] | None = None
    key_members: dict[str, bytes] = {}
    if key_path.is_file() and payload_path is not None and payload_path.is_file():
        key_members, key_inventory = _read_zip(key_path)
        authentication, key_errors, signed_properties, key_members = _inspect_key_members(
            key_members, key_inventory, payload_members
        )
        errors.extend(key_errors)
    else:
        errors.append("fixed sibling prog/jars/key.jar")
        authentication = {
            "certificate_parse_errors": [],
            "certificates": [],
            "digest_mismatches": 0,
            "digest_records_checked": 0,
            "key_jar_inventory": [],
            "manifest_digest_matches": False,
            "missing_named_members": [],
            "payload_members_covered": 0,
            "same_name_member_mismatches": [],
            "signature_blocks": [],
            "signature_files": [],
            "signature_math_verified": False,
            "signed_descriptor_covered": False,
            "uncovered_payload_members": sorted(payload_members),
        }

    incoming_transformation = _inverse_transformation_report(payload_members, key_members)
    if (
        key_path.is_file()
        and payload_path is not None
        and payload_path.is_file()
        and not incoming_transformation["consistent_with_ams_split"]
    ):
        errors.append("installed payload/key pair is inconsistent with AMS split")

    identity = _identity_report(installed, signed_properties)
    if signed_properties is not None:
        for key in _PROTECTED_DESCRIPTOR_KEYS:
            if (key in installed or key in signed_properties) and installed.get(key) != signed_properties.get(key):
                errors.append("signed and installed %s differ" % key)

    errors = sorted(set(errors))
    key_missing = "fixed sibling prog/jars/key.jar" in errors
    payload_descriptor_missing = "executable JAR root xlet.properties" in errors
    valid = not errors
    if valid:
        classification = "factory-installed-layout-analogue"
    elif (key_missing or payload_descriptor_missing) and all(
        item in ("fixed sibling prog/jars/key.jar", "executable JAR root xlet.properties")
        for item in errors
    ):
        classification = "incomplete-installed-layout-skeleton"
    else:
        classification = "invalid-installed-layout"

    missing = _base_installability()
    if key_missing:
        missing.insert(0, "legitimate detached key.jar envelope")
    if payload_descriptor_missing:
        missing.insert(0, "payload-root signed xlet.properties")
    report: dict[str, Any] = {
        "application": {
            "app_id": app_id,
            "jar_file": jar_file,
            "main_class": installed.get("xlet.mainClass"),
            "name": installed.get("xlet.name"),
            "vendor": installed.get("xlet.vendor"),
            "version": installed.get("xlet.version"),
        },
        "authentication": authentication,
        "classification": classification,
        "container": {
            "accepted_schema": "STRUCTURALLY_CONFORMING" if valid else "NONCONFORMING",
            "candidate_conforms": valid,
            "input_name": root.name,
            "schema_contract": "PROVED for factory layout and AMS incoming member routing",
            "type": "directory",
        },
        "descriptor": {
            "installed_sha256": _sha256(installed_data),
            "payload_root_present": payload_descriptor_data is not None,
            "payload_root_sha256": (
                _sha256(payload_descriptor_data)
                if payload_descriptor_data is not None
                else None
            ),
            "property_keys": sorted(installed),
            "signed_property_keys": sorted(signed_properties) if signed_properties else [],
        },
        "entitlements": _entitlement_report(signed_properties or installed),
        "identity": identity,
        "incoming_transformation": incoming_transformation,
        "installability": {
            "installable": False,
            "missing_requirements": missing,
            "status": "NON-INSTALLABLE / RESEARCH INSPECTION; TRUST NOT VERIFIED",
        },
        "payload": {
            "inventory": payload_inventory,
            "member_count": len(payload_inventory),
            "sha256": payload_sha,
            "size": payload_size,
        },
        "structure": {
            "errors": errors,
            "structurally_analogous_to_stock": valid,
            "valid": valid,
        },
    }
    if hello_profile:
        report["hello_profile"] = _hello_profile(installed, signed_properties)
    return report


def _inspect_single_jar(path: Path, hello_profile: bool) -> dict[str, Any]:
    data = path.read_bytes()
    if not data.startswith(b"PK\x03\x04"):
        raise PackageInspectionError("single package candidate has no ZIP/JAR magic")
    members, inventory = _read_zip(path)
    descriptor_data = members.get("xlet.properties")
    properties = parse_java_properties(descriptor_data) if descriptor_data is not None else {}
    signature_files = sorted(name for name in members if _AMS_SIGNATURE_FILE.match(name))
    signature_blocks = sorted(name for name in members if _AMS_SIGNATURE_BLOCK.match(name))
    signature_stems = {
        _AMS_SIGNATURE_FILE.match(name).group(1) for name in signature_files
    }
    block_stems = {
        _AMS_SIGNATURE_BLOCK.match(name).group(1) for name in signature_blocks
    }
    token_properties = sorted(
        key
        for key in ("xlet.developerToken", "xlet.deviceToken")
        if properties.get(key)
    )
    developer_token_present = "xlet.developerToken" in token_properties
    device_token_present = "xlet.deviceToken" in token_properties
    conventional_signature_shape = (
        "META-INF/MANIFEST.MF" in members
        and bool(signature_stems)
        and signature_stems == block_stems
    )
    errors: list[str] = []
    if descriptor_data is None:
        errors.append("root xlet.properties")
    for key in ("xlet.appId", "xlet.jarFile", "xlet.mainClass", "xlet.name", "xlet.version"):
        if not properties.get(key):
            errors.append("descriptor missing %s" % key)
    if properties.get("xlet.appId") and not _ams_app_id_valid(properties.get("xlet.appId")):
        errors.append("xlet.appId uses characters rejected by AMS")
    if properties.get("xlet.appId") and not is_safe_leaf_name(properties["xlet.appId"]):
        errors.append("xlet.appId is not a safe directory leaf")
    if not conventional_signature_shape:
        if developer_token_present:
            errors.append("token-only authentication profile is not recovered")
        else:
            errors.append("conventional JAR signature metadata")
    transformation = _single_jar_transformation_report(members)
    authentication: dict[str, Any]
    if conventional_signature_shape:
        predicted_payload = {
            name: data for name, data in members.items() if not _ams_routes_to_key(name)
        }
        predicted_key = {
            name: data
            for name, data in members.items()
            if _ams_routes_to_key(name) or name == "xlet.properties"
        }
        authentication, authentication_errors, _, _ = _inspect_key_members(
            predicted_key, _inventory_from_members(predicted_key), predicted_payload
        )
        for error in authentication_errors:
            if error.startswith("key.jar "):
                errors.append("incoming JAR " + error[len("key.jar ") :])
            else:
                errors.append("incoming JAR " + error)
        authentication["profile"] = "RECOVERED_CONVENTIONAL_JAR_SIGNATURE"
    else:
        authentication = {
            "certificate_parse_errors": [],
            "certificates": [],
            "profile": (
                "TOKEN_BEARING_PROFILE_NOT_RECOVERED"
                if developer_token_present
                else (
                    "DEVICE_TOKEN_WITHOUT_CONVENTIONAL_SIGNATURE"
                    if device_token_present
                    else "NO_RECOVERED_AUTHENTICATION_PROFILE"
                )
            ),
            "signature_blocks": signature_blocks,
            "signature_files": signature_files,
            "signature_math_verified": False,
            "token_properties_present": token_properties,
        }
    valid = not errors
    if valid:
        classification = "live-incoming-jar-structural-candidate"
    elif descriptor_data is not None and errors == ["token-only authentication profile is not recovered"]:
        classification = "unverified-token-authentication-profile"
    elif descriptor_data is not None and errors == ["conventional JAR signature metadata"]:
        classification = "unsigned-live-schema-fixture"
    else:
        classification = "invalid-live-schema-candidate"
    report: dict[str, Any] = {
        "application": {
            "app_id": properties.get("xlet.appId"),
            "jar_file": properties.get("xlet.jarFile"),
            "main_class": properties.get("xlet.mainClass"),
            "name": properties.get("xlet.name"),
            "vendor": properties.get("xlet.vendor"),
            "version": properties.get("xlet.version"),
        },
        "authentication": authentication,
        "classification": classification,
        "container": {
            "accepted_schema": (
                "STRUCTURALLY_CONFORMING"
                if valid
                else (
                    "AUTHENTICATION_PROFILE_UNKNOWN"
                    if classification == "unverified-token-authentication-profile"
                    else "NONCONFORMING"
                )
            ),
            "candidate_conforms": (
                None
                if classification == "unverified-token-authentication-profile"
                else valid
            ),
            "input_name": path.name,
            "magic_hex": data[:4].hex(),
            "schema_contract": "PROVED",
            "sha256": _sha256(data),
            "size": len(data),
            "type": "zip-jar",
        },
        "descriptor": {
            "embedded_at_root": descriptor_data is not None,
            "property_keys": sorted(properties),
        },
        "entitlements": _entitlement_report(properties),
        "incoming_transformation": transformation,
        "installability": {
            "installable": False,
            "missing_requirements": _base_installability(),
            "status": "STRUCTURAL ANALYSIS ONLY / AUTHORITY NOT VERIFIED",
        },
        "payload": {
            "inventory": inventory,
            "member_count": len(inventory),
        },
        "structure": {
            "errors": sorted(errors),
            "structurally_analogous_to_stock": valid,
            "valid": valid,
        },
    }
    if hello_profile:
        report["hello_profile"] = _hello_profile(properties)
    return report


def inspect_installed_tree(root: Path) -> dict[str, Any]:
    """Inspect every installed application below *root* without changing it."""

    root = Path(root)
    if not root.is_dir():
        raise PackageInspectionError("installed-tree input is not a directory")
    discovered = {path.parent.parent for path in root.rglob("prog/xlet.properties")}
    discovered.update(path.parent for path in root.rglob("prog") if path.is_dir())
    for xlets_dir in root.rglob("xlets"):
        if xlets_dir.is_dir():
            discovered.update(path for path in xlets_dir.iterdir() if path.is_dir())
    app_roots = sorted(discovered, key=lambda path: path.relative_to(root).as_posix())
    records: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for app_root in app_roots:
        relative = app_root.relative_to(root).as_posix()
        try:
            report = _inspect_directory(app_root, False)
        except PackageInspectionError as error:
            failures.append({"error": str(error), "path": relative})
            continue
        transformation = report["incoming_transformation"]
        records.append(
            {
                "app_id": report["application"]["app_id"],
                "classification": report["classification"],
                "content_set_sha256": transformation["content_set_sha256"],
                "key_member_count": len(transformation["key_member_names"]),
                "member_count": transformation["predicted_incoming_member_count"],
                "path": relative,
                "payload_member_count": len(transformation["payload_member_names"]),
                "split_consistent": transformation["consistent_with_ams_split"],
            }
        )

    consistent = sum(record["split_consistent"] for record in records)
    fully_valid = sum(
        record["classification"] == "factory-installed-layout-analogue"
        for record in records
    )
    fingerprints = {
        record["content_set_sha256"]
        for record in records
        if record["content_set_sha256"] is not None
    }
    invalid = len(records) - fully_valid
    census_errors: list[str] = []
    if not app_roots:
        census_errors.append("installed-tree census found no application directories")
    if failures or invalid:
        census_errors.append("installed-tree census contains invalid or unreadable layouts")
    return {
        "ams_split_consistent_instances": consistent,
        "ams_split_inconsistent_instances": len(records) - consistent,
        "application_instances": len(app_roots),
        "fully_valid_installed_layouts": fully_valid,
        "inspection_failures": failures,
        "invalid_installed_layouts": invalid,
        "records": records,
        "structure": {
            "errors": census_errors,
            "valid": bool(app_roots) and not failures and not invalid,
        },
        "unique_content_sets": len(fingerprints),
    }


def inspect_path(path: Path, *, hello_profile: bool = False) -> dict[str, Any]:
    """Inspect a directory or JAR without changing the source artifact."""

    path = Path(path)
    if path.is_dir():
        return _inspect_directory(path, hello_profile)
    if path.is_file():
        return _inspect_single_jar(path, hello_profile)
    raise PackageInspectionError("input path does not exist")


def render_json(report: dict[str, Any], *, pretty: bool = False) -> str:
    return json.dumps(report, indent=2 if pretty else None, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an RA4 installed layout or live single-JAR structural candidate"
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--hello-profile", action="store_true")
    parser.add_argument("--scan-installed-tree", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.scan_installed_tree:
            if args.hello_profile:
                parser.error("--hello-profile cannot be combined with --scan-installed-tree")
            report = inspect_installed_tree(args.path)
        else:
            report = inspect_path(args.path, hello_profile=args.hello_profile)
    except PackageInspectionError as error:
        print("error: %s" % error, file=sys.stderr)
        return 2
    rendered = render_json(report, pretty=args.pretty)
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        try:
            args.output.write_text(rendered, encoding="ascii")
        except OSError as error:
            print("error: cannot write report: %s" % error, file=sys.stderr)
            return 2
    return 0 if report["structure"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
