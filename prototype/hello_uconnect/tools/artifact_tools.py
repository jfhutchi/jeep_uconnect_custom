"""Deterministic packaging and classfile validation for Hello Uconnect.

This module intentionally uses only the Python standard library. It validates
symbolic dependencies; it does not execute Java or recovered target code.
"""

from __future__ import annotations

import hashlib
import json
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


STATUS_MARKER = "HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET"
NATIVE_SUFFIXES = (".so", ".dll", ".dylib", ".jnilib", ".a", ".o")
COMPILE_STUB_PREFIXES = ("javax/microedition/", "com/sun/lwuit/")
DEFAULT_RUNTIME_PREFIXES = (
    "com/aicas/",
    "com/chrysler/",
    "com/fca/",
    "com/harman/",
    "kona/",
)


class ValidationError(ValueError):
    """Raised when an artifact violates a host-side safety/build invariant."""


class _Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def take(self, size: int) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise ValidationError("truncated classfile")
        result = self.data[self.offset:end]
        self.offset = end
        return result

    def u1(self) -> int:
        return self.take(1)[0]

    def u2(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def u4(self) -> int:
        return struct.unpack(">I", self.take(4))[0]


@dataclass(frozen=True)
class ClassAudit:
    name: str
    major: int
    native_methods: int
    invokedynamic_references: int
    class_owners: tuple[str, ...]
    member_references: tuple[tuple[str, str, str], ...]


def _cp_utf8(pool: list[Any], index: int) -> str:
    if index <= 0 or index >= len(pool):
        raise ValidationError("invalid constant-pool index %d" % index)
    entry = pool[index]
    if entry is None or entry[0] != 1:
        raise ValidationError("constant-pool entry %d is not UTF-8" % index)
    return entry[1]


def _cp_class_name(pool: list[Any], index: int) -> str:
    if index <= 0 or index >= len(pool):
        raise ValidationError("invalid class constant-pool index %d" % index)
    entry = pool[index]
    if entry is None or entry[0] != 7:
        raise ValidationError("constant-pool entry %d is not a class" % index)
    return _cp_utf8(pool, entry[1])


def _skip_attributes(reader: _Reader, count: int) -> None:
    for _ in range(count):
        reader.u2()
        reader.take(reader.u4())


def _descriptor_class_owners(descriptor: str) -> set[str]:
    owners = set()
    offset = 0
    while True:
        start = descriptor.find("L", offset)
        if start < 0:
            return owners
        end = descriptor.find(";", start + 1)
        if end < 0:
            raise ValidationError("invalid class descriptor %s" % descriptor)
        owners.add(descriptor[start + 1:end])
        offset = end + 1


def inspect_classfile(data: bytes) -> ClassAudit:
    reader = _Reader(data)
    if reader.take(4) != b"\xca\xfe\xba\xbe":
        raise ValidationError("invalid classfile magic")
    reader.u2()
    major = reader.u2()
    pool_count = reader.u2()
    pool: list[Any] = [None]
    invokedynamic = 0

    index = 1
    while index < pool_count:
        tag = reader.u1()
        if tag == 1:
            length = reader.u2()
            raw = reader.take(length)
            try:
                value = raw.decode("utf-8")
            except UnicodeDecodeError as error:
                raise ValidationError("invalid UTF-8 constant") from error
            pool.append((tag, value))
        elif tag in (3, 4):
            pool.append((tag, reader.take(4)))
        elif tag in (5, 6):
            pool.append((tag, reader.take(8)))
            pool.append(None)
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            pool.append((tag, reader.u2()))
        elif tag in (9, 10, 11, 12, 17, 18):
            pool.append((tag, reader.u2(), reader.u2()))
            if tag == 18:
                invokedynamic += 1
        elif tag == 15:
            pool.append((tag, reader.u1(), reader.u2()))
        else:
            raise ValidationError("unsupported constant-pool tag %d" % tag)
        index += 1

    reader.u2()
    this_class = reader.u2()
    reader.u2()
    class_name = _cp_class_name(pool, this_class)
    for _ in range(reader.u2()):
        reader.u2()
    descriptor_owners: set[str] = set()
    field_count = reader.u2()
    for _ in range(field_count):
        reader.u2()
        reader.u2()
        descriptor_owners.update(_descriptor_class_owners(_cp_utf8(pool, reader.u2())))
        _skip_attributes(reader, reader.u2())

    native_methods = 0
    method_count = reader.u2()
    for _ in range(method_count):
        access_flags = reader.u2()
        reader.u2()
        descriptor_owners.update(_descriptor_class_owners(_cp_utf8(pool, reader.u2())))
        if access_flags & 0x0100:
            native_methods += 1
        _skip_attributes(reader, reader.u2())
    _skip_attributes(reader, reader.u2())
    if reader.offset != len(data):
        raise ValidationError("classfile has %d trailing bytes" % (len(data) - reader.offset))

    class_owners = []
    member_references = []
    for entry in pool[1:]:
        if entry is None:
            continue
        if entry[0] == 7:
            class_owners.append(_cp_utf8(pool, entry[1]))
        elif entry[0] in (9, 10, 11):
            owner = _cp_class_name(pool, entry[1])
            name_type = pool[entry[2]]
            if name_type is None or name_type[0] != 12:
                raise ValidationError("member reference has invalid name-and-type")
            descriptor = _cp_utf8(pool, name_type[2])
            descriptor_owners.update(_descriptor_class_owners(descriptor))
            member_references.append((owner, _cp_utf8(pool, name_type[1]), descriptor))

    return ClassAudit(
        name=class_name,
        major=major,
        native_methods=native_methods,
        invokedynamic_references=invokedynamic,
        class_owners=tuple(sorted(set(class_owners) | descriptor_owners)),
        member_references=tuple(sorted(set(member_references))),
    )


def _normalize_class_owner(owner: str) -> str | None:
    while owner.startswith("["):
        owner = owner[1:]
    if len(owner) == 1:
        return None
    if owner.startswith("L") and owner.endswith(";"):
        return owner[1:-1]
    return owner


def _load_policy(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError("cannot read API allowlist: %s" % error) from error
    required = ("target_major", "application_prefix", "allowed_class_owners", "allowed_members")
    missing = [name for name in required if name not in value]
    if missing:
        raise ValidationError("API allowlist missing: %s" % ", ".join(missing))
    return value


def _member_set(values: Iterable[Iterable[str]]) -> set[tuple[str, str, str]]:
    result = set()
    for value in values:
        item = tuple(value)
        if len(item) != 3 or not all(isinstance(part, str) for part in item):
            raise ValidationError("member allowlist entries must be owner/name/descriptor triples")
        result.add(item)
    return result


def _parse_properties(path: Path) -> tuple[dict[str, str], str]:
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as error:
        raise ValidationError("cannot read descriptor: %s" % error) from error
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        separator = "=" if "=" in line else ":" if ":" in line else None
        if separator is None:
            raise ValidationError("descriptor line %d has no separator" % line_number)
        key, value = (part.strip() for part in line.split(separator, 1))
        if key in values:
            raise ValidationError("duplicate descriptor field %s" % key)
        values[key] = value
    return values, text


def _bool_field(values: dict[str, str], name: str, default: bool | None = None) -> bool:
    if name not in values:
        if default is None:
            raise ValidationError("descriptor missing required field %s" % name)
        return default
    normalized = values[name].lower()
    if normalized not in ("true", "false"):
        raise ValidationError("descriptor field %s is not boolean" % name)
    return normalized == "true"


def validate_descriptor(
    path: Path,
    *,
    expected_main_class: str,
    expected_app_id: str,
) -> dict[str, Any]:
    values, text = _parse_properties(path)
    if STATUS_MARKER not in text:
        raise ValidationError("descriptor lacks unsigned/non-installable status marker")
    if values.get("xlet.mainClass") != expected_main_class:
        raise ValidationError("descriptor main class does not match original Xlet")
    if values.get("xlet.appId") != expected_app_id:
        raise ValidationError("descriptor app ID does not match project identity")

    allowed_fields = {
        "xlet.PauseAllowed",
        "xlet.appId",
        "xlet.daemon",
        "xlet.hasGUI",
        "xlet.headless",
        "xlet.isAudio",
        "xlet.jarFile",
        "xlet.mainClass",
        "xlet.name",
        "xlet.vendor",
        "xlet.version",
    }
    unexpected_fields = sorted(set(values) - allowed_fields)
    if unexpected_fields:
        raise ValidationError(
            "descriptor contains undocumented or privileged fields: %s"
            % ", ".join(unexpected_fields)
        )

    autostart = _bool_field(values, "xlet.autostart", False)
    daemon = _bool_field(values, "xlet.daemon")
    audio_app = _bool_field(values, "xlet.isAudio")
    has_gui = _bool_field(values, "xlet.hasGUI")
    headless = _bool_field(values, "xlet.headless")
    if autostart or daemon or audio_app or not has_gui or headless:
        raise ValidationError("descriptor safety fields are not conservative")

    return {
        "app_id": expected_app_id,
        "main_class": expected_main_class,
        "autostart": autostart,
        "daemon": daemon,
        "audio_app": audio_app,
        "has_gui": has_gui,
        "headless": headless,
        "installable": False,
        "status": STATUS_MARKER,
    }


def write_deterministic_jar(source_dir: Path, destination: Path) -> list[str]:
    source_dir = source_dir.resolve()
    destination = destination.resolve()
    members = sorted(
        path.relative_to(source_dir).as_posix()
        for path in source_dir.rglob("*")
        if path.is_file()
    )
    if not members:
        raise ValidationError("cannot package an empty application JAR")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w") as archive:
        for member in members:
            source_path = source_dir / Path(member)
            info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source_path.read_bytes())
    return members


def audit_artifact(jar_path: Path, descriptor_path: Path, policy_path: Path) -> dict[str, Any]:
    jar_path = Path(jar_path)
    descriptor_path = Path(descriptor_path)
    policy = _load_policy(Path(policy_path))
    target_major = int(policy["target_major"])
    application_prefix = str(policy["application_prefix"])
    allowed_classes = set(str(value) for value in policy["allowed_class_owners"])
    allowed_members = _member_set(policy["allowed_members"])
    required_members = _member_set(policy.get("required_members", ()))
    observed_prefixes = {
        str(category): tuple(str(value) for value in prefixes)
        for category, prefixes in policy.get("observed_owner_prefixes", {}).items()
    }
    prohibited_prefixes = {
        str(category): tuple(str(value) for value in prefixes)
        for category, prefixes in policy.get("prohibited_owner_prefixes", {}).items()
    }
    prohibited_members = {
        str(category): _member_set(values)
        for category, values in policy.get("prohibited_members", {}).items()
    }
    runtime_prefixes = tuple(policy.get("bundled_runtime_prefixes", DEFAULT_RUNTIME_PREFIXES))

    try:
        archive = zipfile.ZipFile(jar_path, "r")
    except (OSError, zipfile.BadZipFile) as error:
        raise ValidationError("cannot read application JAR: %s" % error) from error

    with archive:
        inventory = archive.namelist()
        if len(inventory) != len(set(inventory)):
            raise ValidationError("application JAR contains duplicate members")
        if inventory != sorted(inventory):
            raise ValidationError("application JAR member inventory is not sorted")
        stub_members = [name for name in inventory if name.startswith(COMPILE_STUB_PREFIXES)]
        if stub_members:
            raise ValidationError("application JAR bundles compile stub %s" % stub_members[0])
        runtime_members = [name for name in inventory if name.startswith(runtime_prefixes)]
        if runtime_members:
            raise ValidationError("application JAR bundles vendor runtime %s" % runtime_members[0])
        native_members = [name for name in inventory if name.lower().endswith(NATIVE_SUFFIXES)]
        if native_members:
            raise ValidationError("application JAR contains native library %s" % native_members[0])
        class_members = [name for name in inventory if name.endswith(".class")]
        if not class_members:
            raise ValidationError("application JAR contains no application classes")
        audits = []
        for member_name in class_members:
            audit = inspect_classfile(archive.read(member_name))
            if member_name != audit.name + ".class":
                raise ValidationError(
                    "class path does not match internal owner: %s != %s.class"
                    % (member_name, audit.name)
                )
            audits.append(audit)

    expected_main_owner = str(policy["expected_main_class"]).replace(".", "/")
    if expected_main_owner not in {audit.name for audit in audits}:
        raise ValidationError("descriptor main class is missing from application JAR")

    category_counts = {category: 0 for category in prohibited_prefixes}
    category_counts.update({category: 0 for category in prohibited_members})
    unexpected_references: list[str] = []
    native_method_count = 0
    invokedynamic_count = 0
    all_member_references: set[tuple[str, str, str]] = set()

    for audit in audits:
        if audit.major != target_major:
            raise ValidationError(
                "%s has classfile major %d; required %d"
                % (audit.name, audit.major, target_major)
            )
        if not audit.name.startswith(application_prefix):
            raise ValidationError("unexpected application class owner %s" % audit.name)
        native_method_count += audit.native_methods
        invokedynamic_count += audit.invokedynamic_references
        all_member_references.update(audit.member_references)

        for raw_owner in audit.class_owners:
            owner = _normalize_class_owner(raw_owner)
            if owner is None:
                continue
            for category, prefixes in prohibited_prefixes.items():
                if owner.startswith(prefixes):
                    category_counts[category] += 1
            if owner.startswith(application_prefix) or owner in allowed_classes:
                continue
            if not any(owner.startswith(prefixes) for prefixes in prohibited_prefixes.values()):
                unexpected_references.append("class %s" % owner)

        for member in audit.member_references:
            owner = member[0]
            for category, members in prohibited_members.items():
                if member in members:
                    category_counts[category] += 1
            for category, prefixes in prohibited_prefixes.items():
                if owner.startswith(prefixes):
                    category_counts[category] += 1
            if owner.startswith(application_prefix) or member in allowed_members:
                continue
            if member not in set().union(*prohibited_members.values()) and not any(
                owner.startswith(prefixes) for prefixes in prohibited_prefixes.values()
            ):
                unexpected_references.append("member %s.%s%s" % member)

    if native_method_count:
        raise ValidationError("application contains %d native method(s)" % native_method_count)
    if invokedynamic_count:
        raise ValidationError("application contains %d invokedynamic reference(s)" % invokedynamic_count)
    for category, count in sorted(category_counts.items()):
        if count:
            raise ValidationError("application contains %s reference(s): %d" % (category, count))
    if unexpected_references:
        raise ValidationError("unexpected API member or owner: %s" % unexpected_references[0])
    missing_required = sorted(required_members - all_member_references)
    if missing_required:
        owner, name, descriptor = missing_required[0]
        raise ValidationError(
            "required API member is missing: %s.%s%s" % (owner, name, descriptor)
        )

    observed_counts = {
        category: sum(
            1
            for owner, _name, _descriptor in all_member_references
            if owner.startswith(prefixes)
        )
        for category, prefixes in observed_prefixes.items()
    }

    descriptor = validate_descriptor(
        descriptor_path,
        expected_main_class=policy["expected_main_class"],
        expected_app_id=policy["expected_app_id"],
    )
    jar_bytes = jar_path.read_bytes()
    report = {
        "artifact": {
            "label": str(
                policy.get("artifact_label", "Hello Uconnect host artifact")
            ),
            "jar": jar_path.name,
            "jar_bytes": len(jar_bytes),
            "jar_sha256": hashlib.sha256(jar_bytes).hexdigest(),
            "member_count": len(inventory),
            "inventory": inventory,
            "installed_size_estimate_bytes": len(jar_bytes) + descriptor_path.stat().st_size,
            "installed_size_scope": "application JAR plus draft descriptor; signing/container overhead unknown",
        },
        "bytecode": {
            "application_class_count": len(audits),
            "application_classfile_majors": sorted(set(audit.major for audit in audits)),
            "native_methods": native_method_count,
            "invokedynamic_references": invokedynamic_count,
        },
        "dependencies": {
            "bundled_compile_stubs": len(stub_members),
            "bundled_vendor_runtime_classes": len(runtime_members),
            "custom_native_libraries": len(native_members),
            "jni_references": category_counts.get("jni", 0),
            "prohibited_networking_references": category_counts.get("networking", 0),
            "usb_references": category_counts.get("usb", 0),
            "vehicle_service_references": category_counts.get("vehicle_service", 0),
            "appmanager_privilege_references": category_counts.get("appmanager_privilege", 0),
            "unexpected_api_references": len(unexpected_references),
            "observed_api_references": observed_counts,
            "allowed_member_references": [list(value) for value in sorted(all_member_references)],
        },
        "descriptor": descriptor,
        "installability": (
            "NO - authorized live package issuance, app ID, signer, "
            "principal/policy, and DRM grant unresolved"
        ),
    }
    return report


def write_reports(report: dict[str, Any], output_dir: Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bytecode = {
        "bytecode": report["bytecode"],
        "status": STATUS_MARKER,
    }
    dependencies = {
        "dependencies": report["dependencies"],
        "installability": report["installability"],
        "status": STATUS_MARKER,
    }
    size = {
        key: report["artifact"][key]
        for key in ("jar_bytes", "installed_size_estimate_bytes", "installed_size_scope")
    }
    for name, value in (
        ("bytecode-report.json", bytecode),
        ("dependency-report.json", dependencies),
        ("size-report.json", size),
    ):
        (output_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii"
        )
    (output_dir / "jar-inventory.txt").write_text(
        "\n".join(report["artifact"]["inventory"]) + "\n", encoding="ascii"
    )
    (output_dir / "SHA256SUMS").write_text(
        "%s  %s\n"
        % (report["artifact"]["jar_sha256"], report["artifact"]["jar"]),
        encoding="ascii",
    )
    summary = [
        STATUS_MARKER,
        "",
        report["artifact"]["label"],
        "",
        "Application classfile major:        %s" % report["bytecode"]["application_classfile_majors"][0],
        "Application native methods:         %d" % report["bytecode"]["native_methods"],
        "invokedynamic references:           %d" % report["bytecode"]["invokedynamic_references"],
        "Bundled compile stubs:              %d" % report["dependencies"]["bundled_compile_stubs"],
        "Bundled vendor runtime classes:     %d" % report["dependencies"]["bundled_vendor_runtime_classes"],
        "Custom native libraries:            %d" % report["dependencies"]["custom_native_libraries"],
        "JNI references:                     %d" % report["dependencies"]["jni_references"],
        "Prohibited networking references:  %d" % report["dependencies"]["prohibited_networking_references"],
        "USB references:                     %d" % report["dependencies"]["usb_references"],
        "Vehicle-service references:         %d" % report["dependencies"]["vehicle_service_references"],
        "AppManager privilege references:    %d" % report["dependencies"]["appmanager_privilege_references"],
        "Autostart:                          %s" % str(report["descriptor"]["autostart"]).lower(),
        "Daemon:                             %s" % str(report["descriptor"]["daemon"]).lower(),
        "Audio app:                          %s" % str(report["descriptor"]["audio_app"]).lower(),
        "Unexpected API references:          %d" % report["dependencies"]["unexpected_api_references"],
    ]
    for category, count in sorted(
        report["dependencies"].get("observed_api_references", {}).items()
    ):
        label = "Observed %s references:" % category
        summary.append("%-36s%d" % (label, count))
    summary.append("Artifact installability:            %s" % report["installability"])
    (output_dir / "BUILD-STATUS.txt").write_text("\n".join(summary) + "\n", encoding="ascii")
